# Novodo Packages Documentry

Documentry / tutorial for how to use Novodo Packages

## Setup

Download the Novodo Packages setup zip file from the [official website](https://www.novodo.co.uk)

Then extract the zip file and open it

<!-- todo Finish setup documentry -->

## Command Line

### Check Installation Status

Check installation status with:

```bash
nov
```

If installed properly, this should output:

```bash
Novodo Packages v#.#.#.#, from "C:/Users/#####/.novodo/main.py"
```

### Install

Install a package with:

```bash
nov install <user> <repo>
```

This will download the repo from Github

If installing a package from Novodo, just enter the repo like this:

```bash
nov install <repo>
```

### Uninstall

Uninstall a package with:

```bash
nov uninstall <package>
```

If you have packages from different users with the same name, use:

```bash
nov uninstall <user> <package>
```

### Run

After installing a package, run it with:

```bash
nov run <package> <option>
```

If you have packages from different users with the same name, use:

```bash
nov run <user> <package> <option>
```

And assuming there is a "run" file, you can use:

```bash
nov run <package>
```

Note, this will only work on packages with unique names

### Config

You can edit and make changes to your config, these are the different commands:

#### Get config location

To get the path of your config file, use:

```bash
nov config path
```

#### View config

To view the config, use:

```bash
nov config view
```

#### Backup

To backup your config, even when corrupted, use:

```bash
nov config backup
```

#### Token

You can update your Github token to get faster speeds, to do this use the command:

```bash
nov config token <token>
```

#### Reset

Use this to reset all of your config:

```bash
nov config reset
```

And to reset a sepecific part of your config (e.g. ```Github```), use:

```bash
nov config reset Github
```

## Developing

These are the features included for developers

### This Repo

<details style="border-left: 2px solid #474747; padding-left: 5px;">
<summary>Comments</summary>

<details style="margin-left: 30px; border-left: 2px solid #474747; padding-left: 20px;">
<summary style="margin-left: -15px;">Comment formatter</summary>

Inside the ```.vscode``` folder is a task for VS Code that runs the ```comments.py``` script, this simply formats comments to be more equal

These are the arguments and what they do:

- ```.vscode/comments.py``` - The script that python runs

- ```${file}``` - VS Code automatically sets this to the currently focused file (or the Current Working Directory (```${cwd}```) if the ```ormat ALL file comments in dir``` task is selected)

- ```170``` - Sets the width of the comment

- ```r``` - Sets the side that the comment text is aligned to (valid values are ```l``` for left or ```r``` for right)

To use the comment formatter, open the Command Center (```Ctrl``` + ```Shift``` + ```P```) and enter:

```
>Tasks: Run Task
```

And hit ```Enter```, you can now select whether you want to format the current file or all files in the directory using the arrow keys

This will realign any misaligned comments or expand new comments, to make a new comment use any of these syntaxes:

- ```#I=My imports```
    - Becomes ```# I========================= My imports =====I #```

- ```#F = My functions here```
    - Becomes ```# F================== My functions here =====F #```

- ```# V= My global variables```
    - Becomes ```# V================ My global variables =====V #```

- Etc...

---

</details>

<details style="margin-left: 30px; border-left: 2px solid #474747; padding-left: 20px;">
<summary style="margin-left: -15px;">Comment highlighting</summary>

If using the [Better Comments extention](https://marketplace.visualstudio.com/items?itemName=aaron-bond.better-comments) on VS Code, you can add highlighting for different types of comments

To do this, go to:

```
Better Comments > Settings > Edit in settings.json
```

And then in the json file, under the ```better-comments.tags``` key, add the keys:

```json
{
    "tag": "I",
    "color": "#3498DB",
    "strikethrough": false,
    "underline": false,
    "backgroundColor": "transparent",
    "bold": false,
    "italic": false
},
{
    "tag": "M",
    "color": "#fbb31f",
    "strikethrough": false,
    "underline": false,
    "backgroundColor": "transparent",
    "bold": false,
    "italic": false
},
{
    "tag": "R",
    "color": "#f35e7b",
    "strikethrough": false,
    "underline": false,
    "backgroundColor": "transparent",
    "bold": false,
    "italic": false
},
{
    "tag": "F",
    "color": "#71B51B",
    "strikethrough": false,
    "underline": false,
    "backgroundColor": "transparent",
    "bold": false,
    "italic": false
},
{
    "tag": "V",
    "color": "#17BEBB",
    "strikethrough": false,
    "underline": false,
    "backgroundColor": "transparent",
    "bold": false,
    "italic": false
},
{
    "tag": "G",
    "color": "#b172c9",
    "strikethrough": false,
    "underline": false,
    "backgroundColor": "transparent",
    "bold": false,
    "italic": false
},
{
    "tag": "O",
    "color": "#476BD7",
    "strikethrough": false,
    "underline": false,
    "backgroundColor": "transparent",
    "bold": false,
    "italic": false
}
```

Then open the Command Center (```Ctrl``` + ```Shift``` + ```P```) and enter:

```
>Developer: Restart Extension Host
```

And hit ```Enter```, after it restarts, the different highlighting should be working

<details style="margin-left: 15px; border-left: 2px solid #474747; padding-left: 20px;">
<summary style="margin-left: -15px;">Meanings</summary>

These are the meanings of the different letters for the highlighting:

- ```H``` - Header

- ```I``` - Imports

- ```F``` - Functions

- ```V``` - Variables

- ```G``` - Group

- ```?``` - Description

- ```O``` - Other

- ```M``` - Main

- ```R``` - Runs main with error handling

---

</details>

---

</details>

---

</details>

<details style="border-left: 2px solid #474747; padding-left: 5px;">
<summary>Organisation</summary>

All scripts are organised nicely for debugging or other purposes, grouped using the comment features

---

</details>

### Template Repo

All apps uploaded to Novodo packages should be in a specific format, you can find the official template [here](https://www.github.com/NovodoOfficial/novodo-template)

If you want to make an app, read the ```README.md``` file at [the repo](https://www.github.com/NovodoOfficial/novodo-template) for instructions on how to do so
