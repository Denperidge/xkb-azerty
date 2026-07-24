import pugPlugin from "@11ty/eleventy-plugin-pug";
import eleventyAutoCacheBuster from "eleventy-auto-cache-buster";

//import data from "../data/all.min.json" with {type: "json"};
export const config = {
    dir: {
        input: "src",
        output: "dist"
    }
};

export default function (eleventyConfig) {
    eleventyConfig.addPlugin(pugPlugin);
    eleventyConfig.addPlugin(eleventyAutoCacheBuster);

    eleventyConfig.addPassthroughCopy("src/static/");
    eleventyConfig.addPassthroughCopy({
        "../data/all.min.json": "all.min.json",
        "../data/azerty-all.min.json": "azerty-all.min.json",
        "../data/keysyms.min.json": "keysyms.min.json",
        "node_modules/mvp.css/mvp.css": "static/mvp.css"
    })

    //eleventyConfig.addGlobalData("layouts", data)
}
