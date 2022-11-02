import {
	createTableResult,
	arrayToObject,
	resetSaveChange,
	listernerOnchangeTable,
	editableTable,
	sendButtonInit,
} from "./function.js";
const urlParam = new URLSearchParams(window.location.search);
const livre = urlParam.get("livre");
const numPage = urlParam.get("page");
resetSaveChange();

document.querySelector(
	"#pdfViewer"
).src = `static/pdf/${livre}.pdf#page=${numPage}`;

let editButton = document.querySelector("#edit");
let sendButton = document.querySelector("#send");

listernerOnchangeTable(document.querySelector("#table"));

editableTable(editButton);

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
