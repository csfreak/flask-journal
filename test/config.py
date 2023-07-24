# flake8: noqa

test_config = {
    "SECURITY_EMAIL_VALIDATOR_ARGS": {"test_environment": True},
    "SECURITY_PASSWORD_HASH": "plaintext",
    "SQLALCHEMY_DATABASE_URI": "sqlite://",
    "TESTING": True,
    "WTF_CSRF_ENABLED": False,
    "SERVER_NAME": 'localhost',
    "APPLICATION_ROOT": '/',
    "PREFERRED_URL_SCHEME": 'http'
}

security_config = {
    "users": [
        {
            "email": "user1@example.test",
            "password": "user1_password",
            "roles": [
                "admin",
                "user"
            ],
            "active": True
        },
        {
            "email": "user2@example.test",
            "password": "user2_password",
            "roles": [
                "user",
                "manage"
            ],
            "active": True
        },
        {
            "email": "user3@example.test",
            "password": "user3_password",
            "roles": [
                "user",
            ],
            "active": True
        },
        {
            "email": "user4@example.test",
            "password": "user3_password",
            "roles": [
                "user",
            ],
            "active": False
        }
    ],
    "roles": [
        {
            "name": "admin",
            "description": "admin role"
        },
        {
            "name": "manage",
            "description": "manage role"
        },
        {
            "name": "user",
            "description": "user role"
        },
        {
            "name": "test",
            "description": "test role"
        }
    ],
}

view_form_action_buttons = {
    'view': ['edit', 'delete'],
    'new': ['create'],
    'edit': ['update', 'delete'],
    'all': ['create', 'edit', 'update', 'delete', 'undelete']
}

html_test_strings = {
    'button': {
        'edit':
            '<input class="btn btn-primary btn-md mx-3" id="Edit" name="Edit" type="submit" value="Edit">',
        'update':
            '<input class="btn btn-primary btn-md mx-3" id="Update" name="Update" type="submit" value="Update">',
        'create':
            '<input class="btn btn-primary btn-md mx-3" id="Create" name="Create" type="submit" value="Create">',
        'delete':
            '<input class="btn btn-danger btn-md mx-3" id="Delete" name="Delete" type="submit" value="Delete">',
        'undelete':
            '<input class="btn btn-danger btn-md mx-3" id="Undelete" name="Undelete" type="submit" value="Undelete">',
    },
    'title': '<title>Journal - %s</title>',
    'nav': {
        'login': '<a class="dropdown-item" href="/auth/login">Login</a>',
        'register': '<a class="dropdown-item" href="/auth/register">Register</a>',
        'logout': '<a class="dropdown-item" href="/auth/logout">Logout</a>',
        'settings': '<a class="dropdown-item" href="/settings">Settings</a>'
    },
    'security': {
        'error': {
            'generic': '<li class="fs-error-msg">Authentication failed - identity or password/passcode invalid</li>',
            'email_confirm': '<li class="fs-error-msg">Email requires confirmation.</li>',
        }
    },
    'form': {
        'created_at': '<input class="form-control-plaintext  ms-auto" id="Created At" name="Created At" readonly="" type="text" value="%s">',
        'updated_at': '<input class="form-control-plaintext  ms-auto" id="Created At" name="Created At" readonly="" type="text" value="%s">',
        'confirmed_at': '<input class="form-control-plaintext  ms-auto" id="Created At" name="Created At" readonly="" type="text" value="%s">',
        'deleted_at': '<input class="form-control-plaintext  ms-auto" id="Created At" name="Created At" readonly="" type="text" value="%s">',
        'id': '<input id="id" name="id" type="hidden" value="%d">',
        'roles': '<input class="form-control form-control-plaintext" id="Roles" name="Roles" readonly type="text" value="%s">',
        'error': '<div class="invalid-feedback d-block">%s</div>',
    },
    'table': {
        'create': '<button class="btn btn-primary btn-md" onclick="window.location.href=\'%s\';">Create</button>',
        'base': '<table class="table table-striped table-hover">',
        'title': '<th scope="col" class="col-%d">%s</th>',
        'row': '<tr class="" onclick=\'window.location="/tests?id=%d"\'>\n        <th scope="row">%d</th><td>%s</td>\n    </tr>',
        'pager': {
            'form': '<div class="col d-flex flex-row-reverse">\n        \n<form method="get" class="form" role="form">\n    <select name="page_size" class="form-select mx-1 text-secondary border-secondary" aria-label="select page size" onchange="this.form.submit()">\n        <option selected>Page Size</option>\n        <option value="10">10</option>\n        <option value="20">20</option>\n        <option value="30">30</option>\n    </select>\n</form>\n</div>',
            'current_page': '<a class="page-link" href="#">%d</a>',
            'other_page': '<a class="page-link" href="\n    /tests?page=%d">'
        }
    },
    'settings': {
        'select': '<select class="form-select" id="Theme" name="Theme">',
        'selected': '<option selected value="%s">%s</option>',
        'option': '<option value="%s">%s</option>',
        'css': {
            'default': '<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">',
            'bootswatch': '<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootswatch@5.3.0/dist/%s/bootstrap.min.css">'
        }
    }

}
