import pugPlugin from "@11ty/eleventy-plugin-pug";
import eleventyAutoCacheBuster from "eleventy-auto-cache-buster";
import { readFileSync, readdirSync } from "node:fs";
import allLayouts from "../data/all.json" with {type: "json"};

export const config = {
    dir: {
        input: "src",
        output: "dist"
    }
};

export default function (eleventyConfig) {
    eleventyConfig.addGlobalData("base_url", "https://xkb.denperidge.com")

    eleventyConfig.addPlugin(pugPlugin);
    eleventyConfig.addPlugin(eleventyAutoCacheBuster);

    const datafiles = readdirSync("../data/");

    eleventyConfig.addGlobalData("datafiles", datafiles);
    eleventyConfig.addGlobalData("allLayouts", allLayouts);

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
