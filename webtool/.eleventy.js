import pugPlugin from "@11ty/eleventy-plugin-pug";
import eleventyAutoCacheBuster from "eleventy-auto-cache-buster";
import {readFile} from "node:fs/promises";

readFile("../vendor/yazi-keymap-default.toml");




//import data from "../data/all.min.json" with {type: "json"};
export const config = {
    dir: {
        input: "src",
        output: "dist",
    }
};

export default function (eleventyConfig) {
    eleventyConfig.addPlugin(pugPlugin);
    eleventyConfig.addPlugin(eleventyAutoCacheBuster);

    eleventyConfig.addPassthroughCopy("src/static/");
    eleventyConfig.addPassthroughCopy({"../data/all.min.json": "all.min.json"})

    //eleventyConfig.addGlobalData("layouts", data)
}
