let input = document.querySelector("#search");

let listeLangues = [];
let resultSelect = document.querySelector("#resultSelect");
let baseSelect = document.querySelector("#baseSelect");

function listeDesLangue() {
	if (resultSelect.value === "all") {
		return [baseSelect.value].concat(
			listeLangues.filter((e) => e !== baseSelect.value)
		);
	} else {
		return [baseSelect.value, resultSelect.value];
	}
}

let editButton = document.querySelector("#edit");
let sendButton = document.querySelector("#send");
let saveChange = new Map();

function createTableResult(tab) {
	editButton.hidden = false;
	sendButton.hidden = false;
	let listeLangue = listeDesLangue();
	let resultTitle = document.querySelector("#resultTitle");
	resultTitle.innerHTML = "";
	let trTitle = document.createElement("tr");
	for (let langue of listeLangue) {
		let th = document.createElement("th");
		th.innerHTML = langue;
		trTitle.appendChild(th);
	}
	resultTitle.appendChild(trTitle);
	let resultSearch = document.querySelector("#resultSearch");
	resultSearch.innerHTML = "";
	for (let ligne of tab) {
		let tr = document.createElement("tr");
		let [obj] = ligne.values();
		let sens = obj.sens;
		for (let langue of listeLangue) {
			let td = document.createElement("td");
			if (ligne.has(langue)) {
				td.innerHTML = ligne.get(langue).text;
			}
			td.sens = sens;
			td.langue = langue;
			tr.appendChild(td);
		}
		resultSearch.appendChild(tr);
	}
}

function arrayToObject(arr) {
	let tab = [];
	for (let ligne of arr) {
		tmp = new Map();
		for (let element of ligne) {
			tmp.set(element[0], { text: element[1], sens: element[2] });
		}
		tab.push(tmp);
	}
	return tab;
}

function search() {
	let keyword = input.value;
	saveChange = new Map();
	if (keyword !== "") {
		fetch("/search", {
			method: "POST",
			headers: {
				Accept: "application/json",
				"Content-Type": "application/json",
			},
			body: JSON.stringify({
				keyword: keyword.toLowerCase(),
				langueBase: baseSelect.value,
				langueResult: resultSelect.value,
			}),
		})
			.then((resp) => {
				return resp.json();
			})
			.then((json) => {
				createTableResult(arrayToObject(json));
			});
	}
}

document.querySelector("#searchButton").addEventListener("click", search);
document.querySelector("#search").addEventListener("keypress", (event) => {
	if (event.key.toLocaleLowerCase() === "enter") {
		search();
	}
});

document.querySelector("#table").addEventListener("keyup", (event) => {
	if (event.target.tagName.toLowerCase() === "td") {
		let sens = event.target.sens;
		let langue = event.target.langue;
		let text = event.target.innerText;
		if (!saveChange.has(sens)) {
			saveChange.set(sens, new Map());
		}
		saveChange.get(sens).set(langue, text);
	}
});

editButton.addEventListener("click", (_) => {
	for (let th of document.querySelectorAll("td")) {
		th.contentEditable = true;
	}
});

function mapToArray() {
	let res = [];
	for (let sens of saveChange) {
		let reelSens = sens[0];
		for (let element of sens[1]) {
			res.push(element.concat([reelSens]));
		}
	}
	return res;
}

sendButton.addEventListener("click", (_) => {
	fetch("/edit", {
		method: "POST",
		headers: {
			Accept: "application/json",
			"Content-Type": "application/json",
		},
		body: JSON.stringify(mapToArray()),
	}).then((resp) => {
		console.log(resp);
	});
	// .then((json) => {});
});

async function main() {
	let resp = await fetch("/listLangue", {
		method: "GET",
		headers: {
			Accept: "application/json",
			"Content-Type": "application/json",
		},
	});
	listeLangues = await resp.json();
	for (let langue of listeLangues) {
		let tmp = document.createElement("option");
		tmp.innerText = langue;
		baseSelect.appendChild(tmp);
	}
	let tmp = document.createElement("option");
	resultSelect.appendChild(tmp);
	tmp.innerText = "Toutes les langues";
	tmp.value = "all";
	for (let langue of listeLangues) {
		let tmp = document.createElement("option");
		tmp.innerText = langue;
		resultSelect.appendChild(tmp);
	}
}
main();
