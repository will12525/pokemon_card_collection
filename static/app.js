default_image_array = ['10.jpg', '11.jpg', '12.png', '13.png', '14.png', '15.png', '16.png', '1.webp', '2.webp', '3.jpg', '4.jpg', '5.jpg', '6.jpg', '7.jpg', '8.jpg', '9.jpg']

String.prototype.toHHMMSS = function () {
    var sec_num = parseInt(this, 10);
    var hours   = Math.floor(sec_num / 3600);
    var minutes = Math.floor((sec_num - (hours * 3600)) / 60);
    var seconds = sec_num - (hours * 3600) - (minutes * 60);

    if (hours   < 10) {hours   = "0"+hours;}
    if (minutes < 10) {minutes = "0"+minutes;}
    if (seconds < 10) {seconds = "0"+seconds;}
    return hours+":"+minutes+":"+seconds;
};

function formatFloatToTwoDecimals(value) {
    // Handle different input types
    if (typeof value === 'string') {
        // Remove leading/trailing whitespace
        value = value.trim();
        // Try parsing the string as a number
        const parsedValue = parseFloat(value);
        // Check if parsing was successful (returns NaN if not a number)
        if (!isNaN(parsedValue)) {
            return parsedValue;
        }
    } else if (typeof value === 'number') {
        // Check if it's a finite number
        if (Number.isFinite(value)) {
            // If float, convert to two decimal places
            if (value % 1 !== 0) {
                return value.toFixed(2);
            } else {
                // Ensure the number is within safe integer limits
                const safeNumber = Math.floor(Math.max(Number.MIN_SAFE_INTEGER, Math.min(Number.MAX_SAFE_INTEGER, value)));
                return safeNumber;
            }
        }
    }
    // Return 0 as default for any other input type or parsing failure
    return 0;
}

async function updateSpanText(spanElementId, newText) {
  const spanElement = document.getElementById(spanElementId);
  if (spanElement) {
    spanElement.textContent = newText; // Use textContent for plain text updates
  } else {
    console.warn(`Span element with ID "${spanElementId}" not found.`);
  }
}
async function gifted(tcgp_id) {
    var url = "/gifted";
    let data = {
        "tcgp_id": tcgp_id
    };
    let response = await fetch(url, {
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "body": JSON.stringify(data),
    });
    if (!response.ok) {
        throw new Error("HTTP status disconnectChromecast: " + response.status);
    } else {
        let response_data = await response.json();
        console.log(response_data)
    }
}
async function update_have(tcgp_id, state_have) {
    var url = "/update_have";
    let data = {
        "tcgp_id": tcgp_id,
        "state_have": state_have
    };
    console.log(data)
    let response = await fetch(url, {
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "body": JSON.stringify(data),
    });
    if (!response.ok) {
        throw new Error("HTTP status disconnectChromecast: " + response.status);
    } else {
        let response_data = await response.json();
        console.log(response_data)
    }
}
async function update_want(tcgp_id, state_want) {
    var url = "/update_want";
    let data = {
        "tcgp_id": tcgp_id,
        "state_want": state_want
    };
    console.log(data)
    let response = await fetch(url, {
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "body": JSON.stringify(data),
    });
    if (!response.ok) {
        throw new Error("HTTP status disconnectChromecast: " + response.status);
    } else {
        let response_data = await response.json();
        console.log(response_data)
    }
}
async function update_card_index(tcgp_id, card_index) {
    var url = "/update_card_index";
    let data = {
        "tcgp_id": tcgp_id,
        "card_index": card_index
    };
    console.log(data)
    let response = await fetch(url, {
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "body": JSON.stringify(data),
    });
    if (!response.ok) {
        throw new Error("HTTP status disconnectChromecast: " + response.status);
    } else {
        let response_data = await response.json();
        console.log(response_data)
    }
}

async function clear_card_field() {
    document.querySelectorAll('.my-class').forEach(e => e.remove());
    document.getElementById("rainbow_loading_bar").hidden = false
}

function createCardIndexInput(destination_div, id, value, label_name, event_function) {
    // Create the input element
    const new_input = document.createElement("input");
    new_input.classList.add("input_sizing");
    new_input.type = "number";
    new_input.id = label_name + id;
    new_input.min = 1;
    new_input.value = value;
    new_input.addEventListener("change", function(event) {
        event_function(id, parseInt(event.target.value, 10))
    });

    // Create the label element
    const new_label = document.createElement("label");
    //  new_label.classList.add("form-label"); // Add class for styling
    new_label.setAttribute("for", id);
    new_label.textContent = label_name;

    // Append the elements to the div
    destination_div.appendChild(new_label);
    destination_div.appendChild(new_input);
}

async function apply_default_image() {
    this.src = "http://192.168.1.175:8000/images/" + default_image_array[Math.floor(Math.random()*default_image_array.length)];
}

async function update_card_search(response_data) {
    const res = await fetch("static/card_template.html")
    const text = await res.text()

    updateSpanText("total_cards", response_data["count_cards"])
    updateSpanText("have_cards", response_data["count_have"])
    updateSpanText("want_cards", response_data["count_want"])
    updateSpanText("percent_complete", formatFloatToTwoDecimals(response_data["percent_complete"]))
    updateSpanText("have_price", formatFloatToTwoDecimals(response_data["price_have"]))
    updateSpanText("want_price", formatFloatToTwoDecimals(response_data["price_want"]))
    updateSpanText("total_price", formatFloatToTwoDecimals(response_data["sum_price"]))

    const mainContent = document.getElementById("card_container");
    for (const card_data of response_data["set_card_list"]) {
        const newElement = document.createElement("div");
        newElement.className = "col-sm-4 my-class";
        newElement.innerHTML = text;
        newElement.querySelector("#card_header_title").textContent = card_data["card_name"]
        newElement.querySelector("#card_image").src = "/static/card_images/" + card_data['tcgp_id'] + "88.jpg";
        newElement.querySelector("#card_image").onerror = apply_default_image
        newElement.querySelector("#card_name").textContent = card_data["card_name"]
        newElement.querySelector("#card_set").textContent = card_data["set_name"]
        newElement.querySelector("#card_cost").textContent = card_data["price"]
        createCardIndexInput(newElement.querySelector("#card_index_div"), card_data['tcgp_id'], card_data['card_index'], "#", update_card_index)
        createCardIndexInput(newElement.querySelector("#card_have_div"), card_data['tcgp_id'], card_data['state_have'], "Have", update_have)
        createCardIndexInput(newElement.querySelector("#card_want_div"), card_data['tcgp_id'], card_data['state_want'], "Want", update_want)
        card_link = "https://www.tcgplayer.com/product/" + card_data['tcgp_id'] + "/pokmeon-" + card_data['tcgp_path']
        newElement.querySelector("#store_link").setAttribute('href', card_link)
        newElement.querySelector("#card_header_title").setAttribute('href', card_link)

        mainContent.appendChild(newElement)
    }
    document.getElementById("rainbow_loading_bar").hidden = true
}


async function queryDB(data) {
    clear_card_field()
    try {
        const url = "/get_set_card_list";
        let response = await fetch(url, {
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "body": JSON.stringify(data),
        });

        if (!response.ok) {
            throw new Error("HTTP error! status: " + response.status);
        }

        let response_data = await response.json();
        // Now you can use response_data (which holds the parsed JSON)
        // ... your logic to process the data ...
        update_card_search(response_data)

    } catch (error) {
        console.error("Error fetching data:", error);
        // Handle errors appropriately (display message, retry, etc.)
    }
}
async function applySortFilter(filter_str) {
    let data = {
        "set_name": document.getElementById("primary_card_set_title").innerText,
        "filter_str": filter_str,
        "card_name_search_query": document.getElementById("card_name_search_query_text_field").value,
        "card_season_search_query": document.getElementById("card_season_search_query_text_field").value,
        "filter_ownership": document.getElementById("filter_ownership").textContent
    };
    queryDB(data)
    updateSpanText("sort_by_selected_item", filter_str)
}
async function applySearchTerm() {
    let data = {
        "set_name": document.getElementById("primary_card_set_title").innerText,
        "filter_str": document.getElementById("sort_by_selected_item").textContent,
        "card_name_search_query": document.getElementById("card_name_search_query_text_field").value,
        "card_season_search_query": document.getElementById("card_season_search_query_text_field").value,
        "filter_ownership": document.getElementById("filter_ownership").textContent
    };
    queryDB(data)
}
async function applySeasonSearchTerm() {
    let data = {
        "set_name": document.getElementById("primary_card_set_title").innerText,
        "filter_str": document.getElementById("sort_by_selected_item").textContent,
        "card_name_search_query": document.getElementById("card_name_search_query_text_field").value,
        "card_season_search_query": document.getElementById("card_season_search_query_text_field").value,
        "filter_ownership": document.getElementById("filter_ownership").textContent
    };
    queryDB(data)
}
async function applyFilterOwnership(filter_ownership) {
    let data = {
        "set_name": document.getElementById("primary_card_set_title").innerText,
        "filter_str": document.getElementById("sort_by_selected_item").textContent,
        "card_name_search_query": document.getElementById("card_name_search_query_text_field").value,
        "card_season_search_query": document.getElementById("card_season_search_query_text_field").value,
        "filter_ownership": filter_ownership
    };
    updateSpanText("filter_ownership", filter_ownership)
    queryDB(data)
}
async function getSetCardList(set_name) {
    let data = {
        "set_name": set_name,
        "filter_str": document.getElementById("sort_by_selected_item").textContent,
        "card_name_search_query": document.getElementById("card_name_search_query_text_field").value,
        "card_season_search_query": document.getElementById("card_season_search_query_text_field").value,
        "filter_ownership": document.getElementById("filter_ownership").textContent
    };
    queryDB(data)
    document.getElementById("primary_card_set_title").textContent = set_name;
};

document.addEventListener("DOMContentLoaded", function(event){

    let data = {
        "set_name": "",
        "filter_str": document.getElementById("sort_by_selected_item").textContent,
        "card_name_search_query": "",
        "filter_ownership": "want"
    };
    console.log(data)
    queryDB(data)

});



