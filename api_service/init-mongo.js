db.createUser(
    {
        user: "mongo_user",
        pwd: "mongo_password",
        roles: [
            {
                role: "readWrite",
                db: "url_service_db"
            }
        ]
    }
);
