"""Frappe tối giản để test thuần Python — KHÔNG cần bench/site.

Chỉ mô phỏng đúng phần API mà `vanphat_portal.api.*` gọi tới:
`utils.flt/parse_json/today/add_days`, `db.get_list/get_value/exists/count/commit`,
`get_doc`, `throw`, `has_permission`, `defaults`, `cache`, `logger`, `session`.

Mục đích: test đặc tả (characterization) cho các hàm thuần/một-doc trước và sau
refactor. Test chạy bằng unittest + `state` điều khiển dữ liệu giả.
Không mô phỏng pypika/qb — endpoint dùng qb thật (list_orders, item.get_list)
phải verify trên bench/site.
"""

import json
from types import SimpleNamespace

TODAY = "2026-01-01"
_MODULE = None


class FrappeThrow(Exception):
	"""Đại diện `frappe.throw` — test bắt lỗi nghiệp vụ bằng except FrappeThrow."""

	def __init__(self, message, exc=None):
		super().__init__(message)
		self.message = message
		self.exc = exc


class DoesNotExistError(Exception):
	pass


class PermissionError_(Exception):
	pass


class Flags(dict):
	def __getattr__(self, name):
		return self.get(name, False)

	def __setattr__(self, name, value):
		self[name] = value


class FakeDoc:
	"""Doc giả: truy cập thuộc tính như frappe.model.document.Document."""

	def __init__(self, data=None, state=None, doctype=None):
		object.__setattr__(self, "_data", dict(data or {}))
		object.__setattr__(self, "flags", Flags())
		object.__setattr__(self, "_state", state)
		object.__setattr__(self, "_comments", [])
		if doctype:
			self._data.setdefault("doctype", doctype)
		self._data.setdefault("name", self._data.get("name") or f"FAKE-{id(self) & 0xFFFF}")
		self._wrap_children()

	def _wrap_children(self):
		for key, value in list(self._data.items()):
			if isinstance(value, list) and value and isinstance(value[0], dict):
				self._data[key] = [FakeDoc(row, self._state) for row in value]

	def __getattr__(self, name):
		try:
			return object.__getattribute__(self, "_data")[name]
		except KeyError as exc:
			raise AttributeError(name) from exc

	def __setattr__(self, name, value):
		if name in ("flags", "_data", "_state", "_comments"):
			object.__setattr__(self, name, value)
		else:
			self._data[name] = value

	def get(self, key, default=None):
		return self._data.get(key, default)

	def as_dict(self):
		return dict(self._data)

	def run_method(self, method, *args, **kwargs):
		handler = getattr(self, "_run_" + method, None)
		if handler:
			return handler(*args, **kwargs)
		return None

	# --- mô phỏng native calculate_taxes_and_totals cho Quotation/Sales Order ---
	def _run_calculate_taxes_and_totals(self):
		total = sum(flt(row.get("qty")) * flt(row.get("rate")) for row in self._data.get("items", []))
		self._data["total"] = total
		template = self._data.get("taxes_and_charges")
		rate = self._state.tax_templates.get(template, 0.0) if self._state and template else 0.0
		self._data["total_taxes_and_charges"] = round(total * rate, 2)
		self._data["grand_total"] = total + self._data["total_taxes_and_charges"]
		return self._data["grand_total"]

	def _run_calculate_totals(self):
		return self._run_calculate_taxes_and_totals()

	def add_comment(self, comment_type, text=None, **kwargs):
		self._comments.append({"comment_type": comment_type, "text": text})
		return SimpleNamespace(name=f"COMMENT-{len(self._comments)}")

	def set_missing_values(self):
		return self

	def db_set(self, field, value=None):
		fields = dict(field) if isinstance(field, dict) else {field: value}
		self._data.update(fields)
		if self._state:
			self._state.writes.append((self._data.get("doctype"), self._data.get("name"), fields))
			for row in self._state.rows.get(self._data.get("doctype"), []):
				if row.get("name") == self._data.get("name"):
					row.update(fields)
		return self

	def reload(self):
		return self

	def submit(self):
		self._data["docstatus"] = 1
		self._data["status"] = "Submitted"
		if self._state:
			self.db_set({"docstatus": 1, "status": "Submitted"})
		return self

	def insert(self):
		self._data.setdefault("docstatus", 0)
		self._data.setdefault("status", "Draft")
		if self._data.get("items"):
			self._run_calculate_taxes_and_totals()
		if self._state:
			self._state.writes.append((self._data.get("doctype"), self._data.get("name"), {"insert": True}))
			self._state.inserted.append(self._data)
		return self

	def declare_enquiry_lost(self, *args, **kwargs):
		self._data["status"] = "Lost"
		return self


class State:
	"""Dữ liệu giả + log lời gọi. Test điều khiển trực tiếp."""

	def __init__(self):
		self.rows = {}
		self.docs = {}
		self.permission = True
		self.roles = ["System Manager"]
		self.defaults = {"Company": "Bao Bì Vạn Phát"}
		self.tax_templates = {}
		self.writes = []
		self.inserted = []
		self.logs = []
		self.calls = []
		self.singles = {("Van Phat Settings", "default_deposit_pct"): 50.0}

	def set_single(self, doctype, field, value):
		"""Ghi Single giả (None = mô phỏng Single/field thiếu)."""
		self.singles[(doctype, field)] = value
		return self

	def add(self, doctype, *rows):
		self.rows.setdefault(doctype, []).extend(rows)
		return self

	def doc(self, doctype, name):
		self.docs[(doctype, name)] = True
		return self

	def set_select_options(self, doctype, fieldname, options):
		"""Options của Custom Field Select native (cho get_print_config test)."""
		if not hasattr(self, "custom_options"):
			self.custom_options = {}
		self.custom_options[(doctype, fieldname)] = options
		return self


def flt(value, precision=None):
	try:
		out = float(value or 0)
	except (TypeError, ValueError):
		out = 0.0
	return round(out, precision) if precision is not None else out


class _DB:
	def __init__(self, state):
		self._state = state

	def _match(self, doctype, filters):
		rows = self._state.rows.get(doctype, [])
		if filters is None:
			return list(rows)
		if isinstance(filters, str):
			return [r for r in rows if r.get("name") == filters]
		if isinstance(filters, dict):
			out = []
			for row in rows:
				if all(_row_matches(row, key, value) for key, value in filters.items()):
					out.append(row)
			return out
		return []  # Criterion (qb) — không mô phỏng

	def get_list(
		self,
		doctype,
		filters=None,
		or_filters=None,
		fields=None,
		order_by=None,
		start=0,
		page_length=None,
		**kwargs,
	):
		self._state.calls.append(("get_list", doctype, {"filters": filters, "or_filters": or_filters}))
		rows = self._match(doctype, filters)
		if or_filters:
			rows = [row for row in rows if any(_or_match(row, f) for f in or_filters)]
		if isinstance(order_by, str) and order_by:
			parts = order_by.split()
			key = parts[0]
			reverse = len(parts) > 1 and parts[1].lower() == "desc"
			rows = sorted(rows, key=lambda r: (r.get(key) is None, r.get(key)), reverse=reverse)
		if start:
			rows = rows[int(start):]
		if page_length:
			rows = rows[: int(page_length)]
		if not fields:
			return [{"name": row.get("name")} for row in rows]
		return [{field: row.get(field) for field in fields} for row in rows]

	def get_value(self, doctype, filters, fieldname=None, as_dict=False, **kwargs):
		self._state.calls.append(("get_value", doctype, filters))
		rows = self._match(doctype, filters)
		if not rows:
			return None
		row = rows[0]
		if isinstance(fieldname, (list, tuple)):
			picked = {field: row.get(field) for field in fieldname}
			return picked if as_dict else tuple(picked[field] for field in fieldname)
		return row.get(fieldname)

	def exists(self, doctype, name=None):
		rows = self._state.rows.get(doctype, [])
		if isinstance(name, dict):
			return any(all(r.get(k) == v for k, v in name.items()) for r in rows)
		return any(r.get("name") == name for r in rows)

	def count(self, doctype, filters=None, **kwargs):
		self._state.calls.append(("count", doctype, filters))
		return len(self._match(doctype, filters))

	def set_value(self, doctype, name, fieldname, value=None, **kwargs):
		self._state.writes.append((doctype, name, fieldname, value))
		fields = fieldname if isinstance(fieldname, dict) else {fieldname: value}
		for row in self._state.rows.get(doctype, []):
			if row.get("name") == name:
				row.update(fields)
		return None

	def commit(self):
		self._state.calls.append(("commit", None, None))
		return None

	def rollback(self):
		return None

	def get_single_value(self, doctype, fieldname, **kwargs):
		"""Đọc Single giả từ `state.singles[(doctype, field)]` (mặc định None)."""
		self._state.calls.append(("get_single_value", doctype, fieldname))
		return (self._state.singles or {}).get((doctype, fieldname))


def _row_matches(row, key, value):
	if isinstance(value, (list, tuple)) and len(value) == 2:
		op, operand = str(value[0]).lower(), value[1]
		actual = row.get(key)
		if op == "like":
			return str(operand).strip("%").lower() in str(actual or "").lower()
		if op == "in":
			return actual in operand
		if op == ">":
			return flt(actual) > flt(operand)
		if op == "<":
			return flt(actual) < flt(operand)
	return row.get(key) == value


def _or_match(row, spec):
	if len(spec) == 4:
		_, field, op, value = spec
	elif len(spec) == 3:
		field, op, value = spec
	else:
		return False
	return _row_matches(row, field, [op, value])


class _Meta:
	"""Meta giả: đọc options của Custom Field Select từ state.custom_options."""

	def __init__(self, state, doctype):
		self._state = state
		self._doctype = doctype

	def get_field(self, fieldname):
		from types import SimpleNamespace

		options = (self._state.custom_options or {}).get((self._doctype, fieldname), "")
		return SimpleNamespace(options=options)


class _Cache:
	def __init__(self, state):
		self._state = state
		self._store = {}

	def get_value(self, key, **kwargs):
		return self._store.get(key)

	def set_value(self, key, value, **kwargs):
		self._store[key] = value
		return value

	def delete_keys(self, pattern):
		prefix = pattern.rstrip("*")
		for key in list(self._store):
			if key.startswith(prefix):
				del self._store[key]
		return None


class _Logger:
	def __init__(self, state):
		self._state = state

	def _record(self, level, message, args):
		self._state.logs.append((level, f"{message} {args}" if args else str(message)))

	def warning(self, message, *args, **kwargs):
		self._record("warning", message, args)

	def info(self, message, *args, **kwargs):
		self._record("info", message, args)

	def error(self, message, *args, **kwargs):
		self._record("error", message, args)


class _QB:
	"""Chỉ đủ để `frappe.qb.DocType` không nổ khi import; pypika thật không có ở đây."""

	def DocType(self, *args, **kwargs):
		raise NotImplementedError("frappe.qb không được mô phỏng trong test thuần")


def install(state=None):
	"""Cài module `frappe` giả vào sys.modules (mutate tại chỗ để giữ identity).

Module api đã `import frappe` từ trước vẫn thấy state mới → mỗi test tự dựng
dữ liệu riêng mà không cần reload module. Trả về (frappe, state).
"""
	import sys
	import types

	global _MODULE
	if _MODULE is None:
		_MODULE = types.ModuleType("frappe")
		sys.modules["frappe"] = _MODULE
	frappe = _MODULE
	state = state or State()
	utils = SimpleNamespace(
		flt=flt,
		parse_json=lambda value: json.loads(value) if isinstance(value, str) else value,
		today=lambda: TODAY,
		add_days=lambda date, days: TODAY,
	)
	frappe.utils = utils
	frappe.db = _DB(state)
	frappe._state = state
	frappe.DoesNotExistError = DoesNotExistError
	frappe.PermissionError = PermissionError_
	frappe.ValidationError = Exception
	frappe.defaults = SimpleNamespace(get_user_default=lambda key: state.defaults.get(key))
	frappe.has_permission = lambda *args, **kwargs: state.permission
	frappe.get_roles = lambda *args, **kwargs: list(state.roles)
	frappe.cache = lambda: _Cache(state)
	frappe.logger = lambda name=None: _Logger(state)
	frappe.session = SimpleNamespace(user="tester@vanphat.com")
	frappe.sessions = SimpleNamespace(get_csrf_token=lambda: "csrf-test")
	frappe.qb = _QB()
	frappe.whitelist = lambda *args, **kwargs: (lambda fn: fn)
	frappe.query_builder = SimpleNamespace(functions=SimpleNamespace(Count=lambda *a, **k: None))
	frappe.get_all = lambda *args, **kwargs: []

	def get_doc(*args, **kwargs):
		if args and isinstance(args[0], dict):
			payload = dict(args[0])
			return FakeDoc(payload, state, payload.get("doctype"))
		doctype = args[0]
		name = args[1] if len(args) > 1 else kwargs.get("name")
		rows = [row for row in state.rows.get(doctype, []) if row.get("name") == name]
		if not rows:
			raise FrappeThrow(f"{doctype} {name} không tồn tại")
		return FakeDoc(rows[0], state, doctype)

	def throw(message, exc=None):
		raise FrappeThrow(message, exc)

	frappe.get_doc = get_doc
	frappe.throw = throw
	frappe.parse_json = utils.parse_json
	frappe.get_list = frappe.db.get_list
	frappe.get_meta = lambda doctype: _Meta(state, doctype)
	return frappe, state
