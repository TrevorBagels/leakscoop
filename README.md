# leakscoop

perform queries across multiple databases, where the field names and the field content structure in each database may vary.


Suppose you've got two database collections, "leak 1" and "leak 2"


In `leak 1`, the schema looks like this:
```
FIRST_NAME: "JOHN"
LAST_NAME: "DOE"
```

and in `leak 2`, the schema looks like this:

```
FName: "John"
LName: "Doe"
```

the program lets you write a configuration for each collection, specifying which fields to use for something like "firstname" or "lastname"

It's a work in progress, but so far, it works. It'll probably be easier to understand if you take a look at the config files under `./collections/`

Some more info for how the configurations work can be found in `notes.md`

Example usage:

Find all records of a guy named John Doe.

`python3 -m dev --firstname John --lastname Doe`

Each database will be searched, and results will be put into a new file under `./results/`
