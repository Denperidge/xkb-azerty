import pugPlugin from "@11ty/eleventy-plugin-pug";
import eleventyAutoCacheBuster from "eleventy-auto-cache-buster";
import { readFileSync, readdirSync } from "node:fs";

export const config = {
    dir: {
        input: "src",
        output: "dist"
    }
};


export default function (eleventyConfig) {
    eleventyConfig.addPlugin(pugPlugin);
    eleventyConfig.addPlugin(eleventyAutoCacheBuster);

    eleventyConfig.addTemplate(
        "index.md",
        readFileSync("../README.md", {encoding: "utf-8"}),
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
        "../data/": "data"
    })

    eleventyConfig.addGlobalData("datafiles", readdirSync("../data/"))
}
