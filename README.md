# MediaWiki Client Library for Editing and Revision In Code (MW CLERIC)

River's tools for writing Python scripts for MediaWiki wikis, including the Fandom wiki farm.

For full docs, please see [readthedocs.io](https://mwcleric.readthedocs.io/en/latest/index.html).

This library was originally known as `river_mwclient`, however I renamed it because it has grown beyond the scope of just being tools for myself into a full-fledged library with a lot of utilities that's useful for many people. Thanks to pcj for coming up with the excellent name.

## Install/upgrade:
This library can be installed from PyPI:
```
pip install mwcleric
```

However, for the most up-to-date version including minor changes you may want to pull directly from the repo if I haven't updated PyPI:
```
pip install -U git+https://github.com/RheingoldRiver/mwcleric
```

If you're using PyCharm, press Alt+F12 to open the console and you can install directly to your venv or whatever it's using that way.

## Logging in

Currently, bot passwords are supported; legacy login without bot passwords should also work. If you want to add support for another type of login, I'm happy to merge a PR for it.

If you don't want to log in, you can just create a `WikiClient` / `FandomClient` object and never log in; this is fine if you just want to make Cargo queries etc. However, if you want to edit your wiki, you probably will want to log in.

You can specify a username & password directly in the `AuthCredentials` constructor, or you can set the name of a `user_file`. This user_file will be used as a key to look up either environment variables or a file. If the file doesn't exist, you will be prompted to enter your information.

**TL;DR: you can do nothing and just be prompted to enter your information.**

### Environment variables method

If you're editing via crontab or setting up a Discord bot etc, dealing with files can suck, so you can set up environment variables. These are expected to be:

* `WIKI_USERNAME_%s`
* `WIKI_PASSWORD_%s`

If you use bot passwords, the password should be formatted like `RheingoldRiver@Python`; your username then `@` then the name of your bot password. The password is just your bot password secret.

### Files / interactive method
The interactive method prompts you to enter your username in two parts, first the wiki username, then the bot password name; as well as the bot password secret, and then creates the user configuration file.

The user configuration file is located in the `~/.config/mwcleric` directory on Linux, and in the `%HOMEPATH%\.config\mwcleric` directory on Windows. (`%HOMEPATH%` typically means `C:\Users\[YOUR USERNAME]`).

The name of the file must be formatted as `wiki_account_[NAME].json`, where `[NAME]` is the variable string you will refer to in the code; for example, `wiki_account_bot.json` for the variable string `bot`.

If you want, you can also create a configuration file manually in the same directory as your code, which will override your central configuration file in the `.config` directory. The file would have to be named in the same way (as described above).

The format of any JSON configuration file is:

```json
{
    "username": "ACCOUNT_NAME@BOT_PASSWORD_NAME",
    "password": "BOT_PASSWORD_TOKEN"
}
```
Replace the placeholders (`ACCOUNT_NAME`, `BOT_PASSWORD_NAME`, and `BOT_PASSWORD_TOKEN`) with the actual credentials you want to use.

### Bot password information & best practices
River wrote an entire blog post about this! See https://river.me/blog/bot-passwords/ for more information.

## Editing
For people wanting to edit wikis, `PageModifier` and `TemplateModifier` are the two things most likely to make your life easier. To use them, you subclass and then overwrite methods to modify the page or template as needed, then instantiate the subclass and run. 

For `PageModifier`, you probably want *either* `update_plaintext` *or* `update_wikitext`, not both.
### Copyable code 
Changing the syntax of a template in all pages that use it:
```python
from mwcleric import WikiggClient
from mwcleric.auth_credentials import AuthCredentials
from mwcleric.template_modifier import TemplateModifierBase
from mwparserfromhell.nodes import Template

credentials = AuthCredentials(user_file="me")
site = WikiggClient('gg', credentials=credentials)
summary = 'Bot edit'


class TemplateModifier(TemplateModifierBase):
    def update_template(self, template: Template):
        return


TemplateModifier(site, 'NAME_OF_TEMPLATE',
                 summary=summary).run()
```
Notes about the above example:
 - The value given to the `user_file` parameter in the constructor of `AuthCredentials` is the same as the user variable string in the names of JSON configuration files. So for the code above, the file would be named, or would have to be named, `wiki_account_me.json`.
 - You are advised to provide a more descriptive summary.
 - To instruct the program on how to change the template, you need to implement the `update_template` method of the `TemplateModifier` class, typically by calling various methods of the provided `template` object. [Refer to the MWPFH documentation for more information](https://mwparserfromhell.readthedocs.io/en/latest/api/mwparserfromhell.nodes.html#module-mwparserfromhell.nodes.template).
 - The template name in place of the `TEMPLATEYOUCAREABOUT` uses the same principles as the `{{}}` syntax in wikitext. `Notice` means `Template:Notice`, `:Notice` means the main namespace page `Notice`, `Module:Thing` means the `Module:` namespace page `Thing`.
 - Other parameters to the `TemplateModifier` constructor may be useful. `namespace` (the numeric ID, or, in newer mwcleric version, its name) means only pages from the chosen namespace will be read; `limit` stops the task after reading the specified number of pages (whether or not any of them needed to be changed) and can help if you want to make sure you implemented your modifier correctly before leaving the bot unattended; `lag` specifies the number of seconds to wait between saving edits.

Performing a sitewide find-and-replace in wikitext: 
```python
from mwcleric.wiki_client import WikiClient
from mwcleric.auth_credentials import AuthCredentials
from mwcleric.page_modifier import PageModifierBase

credentials = AuthCredentials(user_file="me")
site = WikiggClient(site='gg', credentials=credentials)
summary = 'Bot edit'


class PageModifier(PageModifierBase):
    def update_plaintext(self, text):
        return text

    def update_wikitext(self, wikitext):
        return


PageModifier(site,
             summary=summary).run()
```

## Troubleshooting
* Permissions errors
    * Are you logged in? To the right account?
    * Did you grant the bot password all of the necessary rights? (Double-check at Special:BotPasswords!)
* Cargo errors
    * Do you have a field name starting with an underscore? You need to alias this to a name without an underscore

## Contributing
PRs are welcome! So far this repo is mostly Fandom-wiki-centric but it definitely doesn't have to stay that way; though contributions to `FandomClient` are also appreciated. Help with documentation & tests is also welcome!
