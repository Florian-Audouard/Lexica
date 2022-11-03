import {
	createTableResult,
	arrayToObject,
	resetSaveChange,
	listernerOnchangeTable,
	sendButtonInit,
} from "./function.js";
const urlParam = new URLSearchParams(window.location.search);
const livre = urlParam.get("livre");
const numPage = parseInt(urlParam.get("page"));
resetSaveChange();

document.querySelector(
	"#pdfViewer"
).src = `static/pdf/${livre}.pdf#page=${numPage}`;

let editButton = document.querySelector("#edit");
let sendButton = document.querySelector("#send");

listernerOnchangeTable(document.querySelector("#table"), editButton);

sendButtonInit(sendButton);

let listeLangue = "";
fetch("/listLangue", {
	method: "POST",
	headers: {
		Accept: "application/json",
		"Content-Type": "application/json",
	},
	body: JSON.stringify({ livre: livre }),
})
	.then((resp) => resp.json())
	.then((json) => {
		listeLangue = json;
	});

fetch("/getPage", {
	method: "POST",
	headers: {
		Accept: "application/json",
		"Content-Type": "application/json",
	},
	body: JSON.stringify({
		livre: livre,
		page: numPage,
	}),
})
	.then((resp) => resp.json())
	.then((json) => {
		createTableResult(
			arrayToObject(json),
			"français",
			listeLangue,
			document.querySelector("#resultTitle"),
			document.querySelector("#resultSearch"),
			false
		);
	});

document.querySelector("#next").onclick = next;
function next() {
	const url = new URL(window.location);
	const newURL = `${url.pathname}?livre=${livre}&page=${numPage + 1}`;
	window.location.href = newURL;
}
document.querySelector("#prev").onclick = prev;
function prev() {
	const url = new URL(window.location);
	if (numPage > 1) {
		const newURL = `${url.pathname}?livre=${livre}&page=${numPage - 1}`;
		window.location.href = newURL;
	}
}

// selectText method taken from http://stackoverflow.com/a/11128179/782034
