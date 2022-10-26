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
let nextButton = document.querySelector("#next");
let prevButton = document.querySelector("#prev");
let saveChange = new Map();

const MAX_SIZE_TABLE = 25;

function createTableResult(tab) {
	editButton.hidden = false;
	sendButton.hidden = false;
	let listeLangue = listeDesLangue();
	let resultTitle = document.querySelector("#resultTitle");
	resultTitle.innerHTML = "";
	let trTitle = document.createElement("tr");
	let th;
	for (let langue of listeLangue) {
		th = document.createElement("th");
		th.innerHTML = langue;
		trTitle.appendChild(th);
	}
	th = document.createElement("th");
	th.innerHTML = "page";
	trTitle.appendChild(th);

	resultTitle.appendChild(trTitle);
	let resultSearch = document.querySelector("#resultSearch");
	resultSearch.innerHTML = "";
	for (let ligne of tab) {
		let tr = document.createElement("tr");
		let [obj] = ligne.values();
		let sens = obj.sens;
		let td;
		for (let langue of listeLangue) {
			td = document.createElement("td");
			if (ligne.has(langue)) {
				td.innerHTML = `<a class="linkHistory" target="_blank" rel="noopener noreferrer" href="historique?sens=${sens}&langue=${langue}">${
					ligne.get(langue).text
				}</a>`;
			}
			td.sens = sens;
			td.langue = langue;
			tr.appendChild(td);
		}
		test = "t";
		td = document.createElement("td");
		num = ligne.get(baseSelect.value).numeroPage;

		td.innerHTML = `<a class="linkPdf" target="_blank" rel="noopener noreferrer" href="static/pdf/hienghene-Fr.pdf#page=${num}">${num}</a>`;
		tr.appendChild(td);

		resultSearch.appendChild(tr);
	}
}
function arrayToObject(arr) {
	let tab = [];
	for (let ligne of arr) {
		tmp = new Map();
		for (let element of ligne) {
			tmp.set(element[0], {
				text: element[1],
				sens: element[2],
				numeroPage: element[3],
			});
		}
		tab.push(tmp);
	}
	return tab;
}
function createPageCount(total, current) {
	const nbPage = Math.trunc(total / MAX_SIZE_TABLE);
	const actualPage = current / MAX_SIZE_TABLE + 1;
	if (actualPage < nbPage) {
		nextButton.hidden = false;
		nextButton.onclick = (_) => {
			search(
				saveKeyword,
				saveLangueBase,
				saveLangueResult,
				actualPage * MAX_SIZE_TABLE
			);
		};
	} else {
		nextButton.hidden = true;
	}
	if (actualPage > 1) {
		prevButton.hidden = false;
		prevButton.onclick = (_) => {
			search(
				saveKeyword,
				saveLangueBase,
				saveLangueResult,
				(actualPage - 2) * MAX_SIZE_TABLE
			);
		};
	} else {
		prevButton.hidden = true;
	}
	const div = document.querySelector("#pageDisplay");
	let beginDiv = "";
	if (actualPage > 2) {
		beginDiv =
			'<span class="clickable" onclick="clickPage(event)">1</span>' +
			"...";
	}
	let end = "";
	if (actualPage < nbPage - 2) {
		end =
			"..." +
			'<span class="clickable" onclick="clickPage(event)">' +
			nbPage +
			"</span>";
	}
	let prev = "";
	if (actualPage - 1 > 0) {
		prev =
			'<span class="clickable" onclick="clickPage(event)">' +
			(actualPage - 1) +
			"</span>";
	}
	let next = "";
	if (actualPage + 1 < nbPage + 1) {
		next =
			'<span class="clickable" onclick="clickPage(event)">' +
			(actualPage + 1) +
			"</span>";
	}
	div.innerHTML =
		beginDiv +
		prev +
		" " +
		'<span style="font-weight: bold;"">' +
		actualPage +
		"</span>" +
		" " +
		next +
		end;
}
function clickPage(event) {
	const num = parseInt(event.target.innerText, 10);
	search(
		saveKeyword,
		saveLangueBase,
		saveLangueResult,
		(num - 1) * MAX_SIZE_TABLE
	);
}
function search(keyword, langueBase, langueResult, offset) {
	pageNum = offset / MAX_SIZE_TABLE + 1;
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
				langueBase: langueBase,
				langueResult: langueResult,
				offset: offset,
			}),
		})
			.then((resp) => {
				return resp.json();
			})
			.then((json) => {
				createPageCount(json.count, offset);
				createTableResult(arrayToObject(json.table));
			});
	}
}
let saveKeyword, saveLangueBase, saveLangueResult, pageNum;
document.querySelector("#searchButton").addEventListener("click", (_) => {
	saveKeyword = input.value;
	saveLangueBase = baseSelect.value;
	saveLangueResult = resultSelect.value;
	search(saveKeyword, saveLangueBase, saveLangueResult, 0);
});
document.querySelector("#search").addEventListener("keypress", (event) => {
	if (event.key.toLocaleLowerCase() === "enter") {
		saveKeyword = input.value;
		saveLangueBase = baseSelect.value;
		saveLangueResult = resultSelect.value;
		search(saveKeyword, saveLangueBase, saveLangueResult, 0);
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
