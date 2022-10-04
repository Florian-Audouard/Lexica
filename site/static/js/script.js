let input = document.querySelector("#search");

document.querySelector("#searchButton").addEventListener("click", (_) => {
	let keyword = input.value;
	if (keyword !== "") {
		fetch("/search", {
			method: "POST",
			headers: {
				Accept: "application/json",
				"Content-Type": "application/json",
			},
			body: JSON.stringify({
				keyword: keyword.toLowerCase(),
			}),
		})
			.then((resp) => {
				return resp.json();
			})
			.then((json) => {
				console.log(json);
			});
	}
});
