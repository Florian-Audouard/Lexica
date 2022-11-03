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
const showBox = urlParam.get("showBox") === "true";

resetSaveChange();

let editButton = document.querySelector("#edit");
let sendButton = document.querySelector("#send");
let checkBox = document.querySelector("#showBox");
checkBox.checked = showBox;
let livreBox = livre + "-rectangle";
let livreStart = livre;
if (showBox) {
	livreStart = livreBox;
}
document.querySelector(
	"#pdfViewer"
).src = `static/pdf/${livreStart}.pdf#page=${numPage}`;

checkBox.addEventListener("click", (event) => {
	if (event.target.checked) {
		document.querySelector(
			"#pdfViewer"
		).src = `static/pdf/${livreBox}.pdf#page=${numPage}`;
	} else {
		document.querySelector(
			"#pdfViewer"
		).src = `static/pdf/${livre}.pdf#page=${numPage}`;
	}
});

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
	// todo ajout capteur de fin de document
	const url = new URL(window.location);
	const newURL = `${url.pathname}?livre=${livre}&page=${
		numPage + 1
	}&showBox=${showBox}`;
	window.location.href = newURL;
}
document.querySelector("#prev").onclick = prev;
function prev() {
	const url = new URL(window.location);
	if (numPage > 1) {
		const newURL = `${url.pathname}?livre=${livre}&page=${
			numPage - 1
		}&showBox=${showBox}`;
		window.location.href = newURL;
	}
}

// selectText method taken from http://stackoverflow.com/a/11128179/782034
