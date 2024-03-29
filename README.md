# Developing

**Important!** **_Do not edit the master branch. It is auto-generated by hugo. 
The default branch for this repo is `source` and all edits should be made to `source` _**

## Get started
1. Install [hugo](https://gohugo.io/)
1. Clone the repo
    ```
     git clone git@github.com:mrc-ide/mrc-ide.github.io.git
    ```
    You will automatically have checked out the `source` branch, which is the default branch for this repo and contains 
    the source code for the hugo site.
1. Make changes on a branch
1. To view changes locally run `hugo server`
1. To publish merged changes, from the `source` branch run
    ```
     ./scripts/publish.sh
    ```
    
## Re-generating the homepage

The homepage template is at `layouts/index.html` and edits to blurbs, 
page structure, styling etc can be made directly there.

The tab content and graphs are generating using a series of python scripts as 
follows, requiring `python3` (3.7 or later):

1. Install requirements with:
    ```bash
    pip3 install -r requirements.txt --user
    ```

1. Set an environment variable `GITHUB_TOKEN` with a PAT for accessing the GitHub api

1. Fetching the data from github is the slowest part and should need to be done infrequently in development, though we'll arrange to do this periodically to refresh the data.

```bash
./scripts/run_fetch
```

1. Parse the DESCRIPTION files, which requires an R installation

```bash
./scripts/run_parse_description
```
1. Generate a json file containing metadata in a format that we will use

```bash
./scripts/run_generate_json
```

1. Generate json files containing focal graphs (e.g. odin, orderly ecosystems):

```bash
python3 ./scripts/run_generate_graphs 
```
