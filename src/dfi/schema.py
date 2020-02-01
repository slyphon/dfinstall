from marshmallow import Schema, fields, ValidationError


class Defaults(Schema):
  conflicting_file_strategy = fields.String()
  conflicting_symlink_strategy = fields.String()
  base_dir = fields.String()
  link_prefix = fields.String()

