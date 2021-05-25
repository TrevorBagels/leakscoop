# leakscoop

Perform queries across multiple MongoDB databases and collections, where the field names and the field content structure in each database may vary.

### The Problem

Suppose you've got two database collections, "leak1" and "leak2"

In `leak1`, the schema looks like this:
```
FIRST_NAME: "JOHN"
LAST_NAME: "DOE"
```

and in `leak2`, the schema looks like this:

```
FName: "John"
LName: "Doe"
```

A simple program to iterate through all your collections and perform queries wouldn't work, because: 
  a) the field names are different. Notice that in `leak1`, the first name field is `FIRST_NAME`, while in `leak2`, the first name field is named `FName`. 
  b) the field values might be structured differently. In `leak1`, everything is captialized. In `leak2`, it's all title-case.

This program lets you write a configuration for each collection, specifying, in JSON, how to query each field. 

It's a work in progress, but so far, it works pretty well. It'll probably be easier to understand if you take a look at the config files under `./collections/`. Each JSON file under `./collections/` should be an array of objects. The program automatically processes all JSON files under that directory.

Some more info for how the configurations work can be found in `notes.md`


## Example Usage:

Find all records of a guy named John Doe.

`python3 -m dev --firstname John --lastname Doe`

Each database will be searched, and results will be put into a new file under `./results/`

Find all records for someone with an address of "1234 NW Long St"
`python3 -m dev --address "1234 NW long st"`

Adding a zipcode to the end, or a state/province might speed up the query (depending on how you index your databases)



