Mix.install([:scrape, :jason])

dom = Scrape.Source.HTTP.get!("https://hexdocs.pm/elixir/api-reference.html")
|> Scrape.Tools.DOM.from_string()

modules = Scrape.Tools.DOM.attrs(dom, "section.details-list div.summary-signature a", "href")
|> Enum.map(fn m -> String.trim_trailing(m, ".html") end)

modulestr = Enum.join(modules, "\", \"")
IO.puts("modules = [\"#{modulestr}\"]")
