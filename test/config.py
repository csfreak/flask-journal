
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
    'title': b'<title>Journal - %s</title>',
    'nav': {
        'login': b'<a class="dropdown-item" href="/auth/login">Login</a>',
        'register': b'<a class="dropdown-item" href="/auth/register">Register</a>',
        'logout': b'<a class="dropdown-item" href="/auth/logout">Logout</a>',
        'settings': b'<a class="dropdown-item" href="/settings">Settings</a>'
    },
    'security': {
        'error': {
            'generic': b'<li class="fs-error-msg">Authentication failed - identity or password/passcode invalid</li>',
            'email_confirm': b'<li class="fs-error-msg">Email requires confirmation.</li>',
        }
    },
    'form': {
        'created_at': b'<input class="form-control-plaintext  ms-auto" id="Created At" name="Created At" readonly="" type="text" value="%s">',
        'updated_at': b'<input class="form-control-plaintext  ms-auto" id="Created At" name="Created At" readonly="" type="text" value="%s">',
        'confirmed_at': b'<input class="form-control-plaintext  ms-auto" id="Created At" name="Created At" readonly="" type="text" value="%s">',
        'deleted_at': b'<input class="form-control-plaintext  ms-auto" id="Created At" name="Created At" readonly="" type="text" value="%s">',
        'id': b'<input id="id" name="id" type="hidden" value="%d">',
        'roles': b'<input class="form-control form-control-plaintext" id="Roles" name="Roles" readonly type="text" value="%s">',
        'error': b'<div class="invalid-feedback d-block">%s</div>',
    }
}
