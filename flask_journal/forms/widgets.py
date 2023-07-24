import typing as t

from markupsafe import Markup
from wtforms import Field
from wtforms.widgets.core import html_params


class PlainTextWidget:

    html_params = staticmethod(html_params)
    validation_attrs = ["required"]

    def __call__(self: t.Self, field: Field, **kwargs: t.Any) -> str:
        kwargs.setdefault("id", field.id)
        kwargs.setdefault("type", 'text')
        out_class = ["form-control-plaintext"]
        for _class in kwargs.pop('class', '').split(' '):
            if "form-control" not in _class:
                out_class.append(_class)

        kwargs['class'] = ' '.join(out_class)
        if "value" not in kwargs:  # pragma: no cover
            kwargs["value"] = field._value()
        flags = getattr(field, "flags", {})
        for k in dir(flags):   # pragma: no cover
            if k in self.validation_attrs and k not in kwargs:
                kwargs[k] = getattr(flags, k)
        return Markup("<input %s readonly>" % self.html_params(name=field.name, **kwargs))
