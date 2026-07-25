import pugPlugin from "@11ty/eleventy-plugin-pug";
import eleventyAutoCacheBuster from "eleventy-auto-cache-buster";
import { readFileSync, readdirSync } from "node:fs";

export const config = {
    dir: {
        input: "src",
        output: "dist"
    }
};

function generateNav(array, id, title, hrefFunc=(val)=>val, textFunc=(val)=>val) {
    const nav = array.map(value => {
        return `<a href="${hrefFunc(value)}"><li>${textFunc(value)}</li></a>`;
    }).join("\n")
    return `<nav aria-labelledby="${id}">
    <h2 id="${id}">${title}</h2>
    <ul>
        ${nav}
    </ul>
</nav>
`
}


export default function (eleventyConfig) {
    eleventyConfig.addPlugin(pugPlugin);
    eleventyConfig.addPlugin(eleventyAutoCacheBuster);

    const datafiles = readdirSync("../data/");
    const recipes = readdirSync("./src/_data/recipes/");

    eleventyConfig.addGlobalData("datafiles", datafiles);

    eleventyConfig.addTemplate(
        "index.md",
        readFileSync("../README.md", {encoding: "utf-8"})
            .replace("## Explanation", `
                ${generateNav(
                    recipes,
                    "recipes",
                    "Recipes",
                    (filename) => filename.replace(".json", ""),
                    (filename) => filename.replace(".json", "")
                )}
                ${generateNav(
                    datafiles,
                    "datafiles",
                    "Data files",
                    (filename) => "data/" + filename,
                    (filename) => filename.replace(/(\.min|)\.json/, "")
                )}
                 <h2>Explanation</h2>`),
        {
            layout: "layout.pug",
        }
    )

    eleventyConfig.addPassthroughCopy("src/static/");
    eleventyConfig.addPassthroughCopy({
        "../data/all.min.json": "all.min.json",
        "../data/azerty-all.min.json": "azerty-all.min.json",
        "../data/keysyms.min.json": "keysyms.min.json",
        "node_modules/mvp.css/mvp.css": "static/mvp.css",
        "../data/": "data",
        "../LICENSE": "LICENSE"
    })

}
