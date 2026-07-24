const input = document.getElementById("input");
const output = document.getElementById("output");
const layout = document.getElementById("layout");

const regexCleanJsonString = /(^"|"$)/g;

let azertyAll;  // azerty-all.json
let keysyms;  // keysyms.json

function parse(text) {
    const selectedLayout = layout.selectedOptions[0].value;
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
            newKey = JSON.stringify(keysyms[newKey]).replaceAll(regexCleanJsonString, "");
            console.log("unicode value: " + newKey)
        }

        if (recipe.outputTemplate) {
            newKey = recipe.outputTemplate.replace("${KEY}", newKey)
        }

        text = text.replace(needle, newKey)
    }   
        // const newValue = azertyAll[layout.selectedOptions[0].value][`AE0${i}`]
        // console.log(newValue)
        // text = text.replace(`"${i}"`, newValue)

    output.value = text;
}

async function init() {
    azertyAll = await (await fetch("/azerty-all.min.json")).json();
    if (recipe.mode != "xkb") {
        keysyms = await (await fetch("/keysyms.min.json")).json();
    }

    input.value = await (await fetch(recipe.url)).text();
    parse(input.value)
}

output.addEventListener("change", (e) => {
    parse(input.value);
});

init();


