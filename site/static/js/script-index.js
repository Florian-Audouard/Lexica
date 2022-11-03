import {
	createTableResult,
	arrayToObject,
	resetSaveChange,
	listernerOnchangeTable,
	sendButtonInit,
} from "./function.js";

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

const MAX_SIZE_TABLE = 25;

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
	resetSaveChange();
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
				createTableResult(
					arrayToObject(json.table),
					baseSelect.value,
					listeDesLangue(),
					document.querySelector("#resultTitle"),
					document.querySelector("#resultSearch")
				);
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

listernerOnchangeTable(document.querySelector("#table"), editButton);

sendButtonInit(sendButton);
async function main() {
	let resp = await fetch("/listLangue", {
		method: "POST",
		headers: {
			Accept: "application/json",
			"Content-Type": "application/json",
		},
		body: JSON.stringify({ livre: "all" }),
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

