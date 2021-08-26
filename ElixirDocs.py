import re
import os
import sublime
import sublime_plugin
import webbrowser

NAMESPACE_RE = re.compile("defmodule\s+([\w+-\.]+).Mix(?:Project|file)\s+do")
VERSION_RE = re.compile("@version\s+\"([\w\+-\.]+)\"")
MDOC_FALSE_RE = re.compile("@moduledoc\s+false")
MODULE_SPLIT_RE = re.compile("(def(?:module|protocol)\s+(?:[\w\.]+)\s+do)")
MODULE_RE = re.compile("def(?:module|protocol)\s+([\w\.]+)\s+do")

class ModuleListInputHandler(sublime_plugin.ListInputHandler):
    def __init__(self, project_root):
        self.deps_data = self.collect_dependency_modules(project_root)

    def name(self):
        # corresponds to the argument name passed to command.run()
        return "url"

    def placeholder(self):
        return "Module name"

    def get_info(self, mix_exs_path):
        try:
            file = open(mix_exs_path)
            filestr = file.read(250)
            version_match = re.search(VERSION_RE, filestr)
            namespace_match = re.search(NAMESPACE_RE, filestr)
            if version_match and namespace_match:
                return {"namespace": namespace_match.group(1), "version": version_match.group(1)}
        except FileNotFoundError:
            return None

    def get_deps(self, path):
        try:
            deps = []
            deps_path = os.path.join(path, "deps")
            for entry in os.listdir(deps_path):
                info = self.get_info(os.path.join(deps_path, entry, "mix.exs"))
                if info:
                    info["path"] = os.path.join(deps_path, entry)
                    deps.append(info)

            return deps
        except FileNotFoundError:
            return []

    def split_into_modules(self, filestr):
        modules = []
        parts = re.split(MODULE_SPLIT_RE, filestr)
        if parts and len(parts) >= 3:
            # remove content before first module
            parts.pop(0)
            count = int(len(parts) / 2)
            for i in range(count):
                modules.append(parts[2*i] + parts[2*i + 1])
        return modules

    def get_module_names(self, filestr, namespace):
        # TODO figure out a nice way to support nested modules
        documented_modules = []
        modules = self.split_into_modules(filestr)

        for module in modules:
            documented = re.search(MDOC_FALSE_RE, module) == None
            if documented:
                name = re.search(MODULE_RE, module).group(1)
                # quick heuristic to remove false matches like examples in docs
                if name == namespace or name.startswith(namespace + ".") or name.startswith("Mix." + namespace) or name.startswith("Mix.Tasks."):
                    documented_modules.append(name)

        return documented_modules

    def get_documented_modules(self, dep_path, namespace):
        # only visit "lib" dir, this make sure we ignore test modules
        lib_path = os.path.join(dep_path, "lib")

        try:
            module_names = []
            for root, dirs, files in os.walk(lib_path):
                for f in files:
                    file = open(os.path.join(root, f))
                    filestr = file.read()
                    modules = self.get_module_names(filestr, namespace)
                    module_names.extend(modules)

            module_names.sort()
            return module_names

        except FileNotFoundError:
            return []

    def elixir_modules(self):
        modules = ["Kernel", "Kernel.SpecialForms", "Atom", "Base", "Bitwise", "Date", "DateTime"]
        return {"name": "Elixir", "base_url": "https://hexdocs.pm/elixir", "namespace": "Elixir", "modules": modules}

    def collect_dependency_modules(self, project_root):
        collected_deps = []

        if project_root:
            deps = self.get_deps(project_root)
            for dep in deps:
                path = dep["path"]
                name = path.split("/")[-1]
                namespace = dep["namespace"]
                version = dep["version"]
                base_url = "https://hexdocs.pm/" + name + "/" + version
                modules = self.get_documented_modules(path, namespace)
                if modules and len(modules) > 0:
                    collected_deps.append({"name": name, "version": version, "base_url": base_url, "namespace": namespace, "modules": modules})

        collected_deps.sort(key=lambda dep: dep["name"])
        return [self.elixir_modules()] + collected_deps

    def list_items(self):
        sublime_build = int(sublime.version())
        items = []
        for dep in self.deps_data:
            for module in dep["modules"]:
                url = dep["base_url"] + "/" + module + ".html"
                display_text = "📑 " + module

                if sublime_build >= 4095:
                    annotation = dep["name"]
                    if "version" in dep:
                        annotation = annotation + " " + dep["version"]
                    item = sublime.ListInputItem(display_text, url, url, annotation)
                    items.append(item)
                else:
                    items.append((display_text, url))

        return items

class ElixirDocsCommand(sublime_plugin.WindowCommand):
    def __init__(self, window):
        self.window = window
        self.settings = sublime.load_settings("ElixirDocs.sublime-settings")
        self.project_root = self.get_project_root()

    def run(self, url):
        webbrowser.open_new_tab(url)

    def input(self, args):
        return ModuleListInputHandler(self.project_root)

    def get_project_root(self):
        open_folders = self.window.folders()
        if open_folders and len(open_folders) > 0:
            return open_folders[0]
