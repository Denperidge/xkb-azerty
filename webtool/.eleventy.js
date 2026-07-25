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
    eleventyConfig.addGlobalData("base_url", "https://xkb.denperidge.com")

    eleventyConfig.addPlugin(pugPlugin);
    eleventyConfig.addPlugin(eleventyAutoCacheBuster);

    const datafiles = readdirSync("../data/");

    eleventyConfig.addGlobalData("datafiles", datafiles);

    eleventyConfig.addTemplate(
        "index.md",
        readFileSync("../README.md", {encoding: "utf-8"}),
        {
            layout: "layout.pug",
            title: "Home",
            description: "A collection of data & config file converters for Azerty users in XKB"
        }
    )

    eleventyConfig.addPassthroughCopy("src/static/");
    eleventyConfig.addPassthroughCopy({
        "node_modules/wingcss/dist/wing.min.css": "static/wing.min.css",
        "../data/": "data",
        "../LICENSE": "LICENSE"
    })

}
