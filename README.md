# ermrest-dbdiagram

Generate ERD (for now just DBLM file) for an ermrest catalog.


## How to use

We have to run the `pg_dump` as the `ermrest` user. So this script assumes that the current user has `sudo` access and can do `sudo su - ermrest`.

1. Make sure nodejs and npm are installed.

2. Install the dependencies

```
npm clean-install
```

3. Execute the `src/index.js` file:

```sh
# all schemas
node src/index.js _ermrest_catalog_3

# one schema
node src/index.js _ermrest_catalog_3 bio

# multiple schemas
node src/index.js _ermrest_catalog_3 bio,vocab
```

4. Copy the content of `output.dbml` to `https://dbdiagram.io/d`