const input = document.getElementById("input");
const output = document.getElementById("output");
const layout = document.getElementById("layout");

// Globals & constants
const REGEX_SURROUNDING_DBLQUOTES = /(^"|"$)/g;

// Files that will be fetched & need caching
let azertyAll;  // azerty-all.json
let keysyms;  // keysyms.json, only fetched if recipe with mode: unicode

// Initialiazing, only run once
async function init() {
    // Get global data
    azertyAll = await (await fetch("/azerty-all.min.json")).json();

    input.value = await (await fetch(recipe.url)).text();
    parse(input.value)
}

// Parser
async function parse(text) {
    const selectedLayout = layout.selectedOptions[0].value;

    // Contents of one of the files in _data/recipes/
    const recipe = JSON.parse(document.getElementById("recipe").value)

    console.log(selectedLayout)
    console.log(azertyAll[selectedLayout])

    const replace = recipe.replace;
    for (const needle of Object.keys(replace)) {
        const locationCode = replace[needle];

        let newKey = azertyAll[selectedLayout].keys[locationCode][0]
        console.log("xkb value: " + newKey)
        if (recipe.mode == "xkb") {
            // No further actions
        } else if (recipe.mode == "unicode") {
            if (keysyms == undefined) {
                keysyms = await (await fetch("/keysyms.min.json")).json();
            }

            newKey = JSON.stringify(keysyms[newKey])
                .replaceAll(REGEX_SURROUNDING_DBLQUOTES, "");
            console.log("unicode value: " + newKey)
        }

        if (recipe.outputTemplate) {
            newKey = recipe.outputTemplate.replace("${KEY}", newKey)
        }

        text = text.replace(needle, newKey)
    }   

    output.value = text;
}

// Run init & add listeners
input.addEventListener("change", (e) => {
    parse(input.value);
});

init();


