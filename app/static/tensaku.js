const btn = document.querySelector("#conform");
const input = document.querySelector("#input");
const list = document.querySelector("#list");
const keigo = document.querySelector("#keigo");
const hankaku = document.querySelector("#hankaku");
const output = document.querySelector("#output");
const table = document.querySelector("#table");

let isHankaku = false;
let isKeigo = false;

btn.addEventListener("click", async () => {
  const problems = document.querySelectorAll(".problems");
  problems.forEach((e) => {
    list.removeChild(e);
  });
  let str = input.value;
  await axios
    .post(`/api?input=${input.value}&isHankaku=${isHankaku ? 1 : 0}&isKeigo=${isKeigo ? 1 : 0}`)
    .then((res) => {
      console.dir(res);
      output.value = res.data.result;
      // res.data.error.map((v) => {
      //   const li = document.createElement("li");
      //   li.classList.add("problems")
      //   const doc = document.createTextNode(v.message ? `${v.message}`:`${v.change} (${v.position})`);
      //   li.appendChild(doc);
      //   list.appendChild(li);
      // })
        table.innerHTML = res.data.diff;
    })
});

// input.addEventListener("input", async () => {
//     output.value = "";
//   const problems = document.querySelectorAll(".problems");
//   problems.forEach((e) => {
//     list.removeChild(e);
//   });
//   let str = input.value;
//   await axios
//     .post(`/api?input=${input.value}&isHankaku=${isHankaku ? 1 : 0}&isKeigo=${isKeigo ? 1 : 0}`)
//     .then((res) => {
//       console.dir(res);
//       output.value = res.data.result;
//       // res.data.error.map((v) => {
//       //   const li = document.createElement("li");
//       //   li.classList.add("problems")
//       //   const doc = document.createTextNode(v.message ? `${v.message}`:`${v.change} (${v.position})`);
//       //   li.appendChild(doc);
//       //   list.appendChild(li);
//       // });
//         table.innerHTML = res.data.diff;
//     })
// });

keigo.addEventListener("change", () => {
    switch (keigo.value) {
        case "0":
            isKeigo = false;
            break;
        case "1":
            isKeigo = true;
            break;
        default:
            return;
    }
});

hankaku.addEventListener("change", () => {
    switch (hankaku.value) {
        case "0":
            isHankaku = false;
            break;
        case "1":
            isHankaku = true;
            break;
        default:
            return;
    }
});