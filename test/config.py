test_config = {
    "SECURITY_EMAIL_VALIDATOR_ARGS": {"test_environment": True},
    "SECURITY_PASSWORD_HASH": "plaintext",
    "SQLALCHEMY_DATABASE_URI": "sqlite://",
    "TESTING": True,
    "WTF_CSRF_ENABLED": False,
    "SERVER_NAME": "localhost",
    "APPLICATION_ROOT": "/",
    "PREFERRED_URL_SCHEME": "http",
    "IS_GUNICORN": False,
}

security_config = {
    "users": [
        {
            "email": "user1@example.test",
            "password": "user1_password",
            "roles": ["admin", "user"],
            "active": True,
        },
        {
            "email": "user2@example.test",
            "password": "user2_password",
            "roles": ["user", "manage"],
            "active": True,
        },
        {
            "email": "user3@example.test",
            "password": "user3_password",
            "roles": [
                "user",
            ],
            "active": True,
        },
        {
            "email": "user4@example.test",
            "password": "user3_password",
            "roles": [
                "user",
            ],
            "active": False,
        },
        {
            "email": "user5@example.test",
            "password": "user4_password",
            "roles": [
                "user",
            ],
            "active": True,
        },
    ],
    "roles": [
        {"name": "admin", "description": "admin role"},
        {"name": "manage", "description": "manage role"},
        {"name": "user", "description": "user role"},
        {"name": "test", "description": "test role"},
    ],
}

view_form_action_buttons = {
    "view": ["edit", "delete"],
    "new": ["create"],
    "edit": ["update", "delete"],
    "all": ["create", "edit", "update", "delete", "undelete"],
}

html_test_strings = {
    "button": {
        "edit": (
            '<input class="btn btn-primary btn-md mx-3" id="Edit" name="Edit"'
            ' type="submit" value="Edit">'
        ),
        "update": (
            '<input class="btn btn-primary btn-md mx-3" id="Update" name="Update"'
            ' type="submit" value="Update">'
        ),
        "create": (
            '<input class="btn btn-primary btn-md mx-3" id="Create" name="Create"'
            ' type="submit" value="Create">'
        ),
        "delete": (
            '<input class="btn btn-danger btn-md mx-3" id="Delete" name="Delete"'
            ' type="submit" value="Delete">'
        ),
        "undelete": (
            '<input class="btn btn-danger btn-md mx-3" id="Undelete" name="Undelete"'
            ' type="submit" value="Undelete">'
        ),
    },
    "title": "<title>Journal - %s</title>",
    "nav": {
        "login": '<a class="dropdown-item" href="/auth/login">Login</a>',
        "register": '<a class="dropdown-item" href="/auth/register">Register</a>',
        "logout": '<a class="dropdown-item" href="/auth/logout">Logout</a>',
        "settings": '<a class="dropdown-item" href="/settings">Settings</a>',
        "roles": '<a class="dropdown-item" href="/roles">Roles</a>',
        "users": '<a class="dropdown-item" href="/users">Users</a>',
        "tags": '<a class="nav-item nav-link" href="/tags">Tags</a>',
        "entries": '<a class="nav-item nav-link" href="/entries">Entries</a>',
    },
    "security": {
        "error": {
            "generic": (
                '<li class="fs-error-msg">Authentication failed - identity or'
                " password/passcode invalid</li>"
            ),
            "email_confirm": (
                '<li class="fs-error-msg">Email requires confirmation.</li>'
            ),
        }
    },
    "form": {
        "created_at": (
            '<input class="form-control-plaintext  ms-auto" id="Created At"'
            ' name="Created At" readonly="" type="text" value="%s">'
        ),
        "updated_at": (
            '<input class="form-control-plaintext  ms-auto" id="Created At"'
            ' name="Created At" readonly="" type="text" value="%s">'
        ),
        "confirmed_at": (
            '<input class="form-control-plaintext  ms-auto" id="Created At"'
            ' name="Created At" readonly="" type="text" value="%s">'
        ),
        "deleted_at": (
            '<input class="form-control-plaintext  ms-auto" id="Created At"'
            ' name="Created At" readonly="" type="text" value="%s">'
        ),
        "id": '<input id="id" name="id" type="hidden" value="%d">',
        "roles": {
            "multiselect": (
                '<select class="form-control form-control-plaintext"'
                ' id="Roles" multiple name="Roles" readonly>'
                "%s</select>"
            ),
            "user": (
                '<option value="1">admin</option>'
                '<option value="2">manage</option>'
                '<option selected value="3">user</option>'
            ),
            "none": (
                '<option value="1">admin</option>'
                '<option value="2">manage</option>'
                '<option value="3">user</option>'
            ),
        },
        "email": (
            '<input class="form-control form-control-plaintext" id="Email" name="Email"'
            ' readonly type="email" value="%s">'
        ),
        "error": '<div class="invalid-feedback d-block">%s</div>',
    },
    "table": {
        "create": (
            '<button class="btn btn-primary btn-md"'
            " onclick=\"window.location.href='%s';\">Create</button>"
        ),
        "base": '<table class="table table-striped table-hover">',
        "title": '<th scope="col" class="col-%d">%s</th>',
        "row_link": '<tr class="" onclick=\'window.location="/tests?id=%d"\'>',
        "row_data": '<th scope="row">%d</th><td>%s</td>',
        "pager": {
            "form": (
                '<div class="col d-flex flex-row-reverse">\n        \n<form'
                ' method="get" class="form" role="form">\n    <select name="page_size"'
                ' class="form-select mx-1 text-secondary border-secondary"'
                ' aria-label="select page size" onchange="this.form.submit()">\n       '
                " <option selected>Page Size</option>\n        <option"
                ' value="10">10</option>\n        <option value="20">20</option>\n     '
                '   <option value="30">30</option>\n    </select>\n</form>\n</div>'
            ),
            "current_page": '<a class="page-link" href="#">%d</a>',
            "other_page": '<a class="page-link" href="\n    /tests?page=%d">',
        },
    },
    "settings": {
        "select": '<select class="form-select" id="Theme" name="Theme">',
        "selected": '<option selected value="%s">%s</option>',
        "option": '<option value="%s">%s</option>',
        "css": {
            "default": (
                '<link rel="stylesheet"'
                ' href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css">'  # noqa: B950
            ),
            "bootswatch": (
                '<link rel="stylesheet"'
                ' href="https://cdn.jsdelivr.net/npm/bootswatch@5.3.2/dist/%s/bootstrap.min.css">'  # noqa: B950
            ),
        },
    },
    "home": {
        "tag_cloud": '<div class="card my-2" id="tag_cloud">\n    <div class="card-body">\n      <h1 class="card-title">Tags</h4> '
    },
}
