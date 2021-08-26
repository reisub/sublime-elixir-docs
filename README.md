# Elixir Docs

A Sublime Text 3/4 plugin for quick navigation to [HexDocs](https://hexdocs.pm) documentation for modules in Elixir and in project dependencies.

![Demo](demo.gif)

## Installing with [Package Control](https://packagecontrol.io/installation)

1. Press `⌘/Ctrl + Shift + P` to open the command palette.
2. Type `Package Control: Install Package` and press enter. Then search for `Elixir Docs`, select the package and hit enter.

## Usage

1. Open up the command palette with `⌘/Ctrl + Shift + P`
2. Select the `Elixir Docs` command to see a filterable list of Elixir modules
3. Once you've found the module you're interested in, hit enter to navigate to the documentation in your default browser

## Known issues

Finding documented modules is done in Python code and is not exact. It's based on regular expressions which operate under certain assumptions.
Because of this, you may not be able to find some modules even though they are documented. You also may find some modules which don't have documentation published on HexDocs.

There is no simple fix for this, to make it better one would need to parse the Elixir code into an AST and use the AST to extract information. Furthermore, one would need a fast way to check whether a module has documentation published on HexDocs.

That being said, this is just a convenience to access (most of) the documentation faster - so I'm not sure it's justified to invest the work in making it 100% correct.

### Nested modules

Nested modules are most likely not going to be shown in the dropdown.

## Contributing

Feedback and contributions are very much welcome. That being said, please don't get upset if I don't get back to you for some time on issues and PRs; life happens :)

By contributing you agree for your work to be published under the [same license](LICENSE).
