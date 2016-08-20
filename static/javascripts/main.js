function myFunction() {
    document.getElementById("myDropdown").classList.toggle("show");
}

window.onclick = function(event) {
  if (!event.target.matches('.dropbtn')) {
    var dropdowns = document.getElementsByClassName("dropdown-content");
    var i;
    for (i = 0; i < dropdowns.length; i++) {
      var openDropdown = dropdowns[i];
      if (openDropdown.classList.contains('show')) {
        openDropdown.classList.remove('show');
      }
    }
  }
}

function isInt(value) {
  return !isNaN(value) &&
         parseInt(Number(value)) == value &&
         !isNaN(parseInt(value, 10));
}

function verify_input() {

  //verify input

  var gene5prime = document.getElementById("5primegene").value;
  var gene5primeloc = document.getElementById("5primeloc").value;
  var gene3prime = document.getElementById("3primegene").value;
  var gene3primeloc = document.getElementById("3primeloc").value;

  if (!gene5prime) {
    var elem = document.getElementById("warningDiv");
    elem.style.visibility = "visible";
    elem.innerHTML="Specify a 5' gene";
    exit();
  }

  if (!gene3prime) {
    var elem = document.getElementById("warningDiv");
    elem.style.visibility = "visible";
    elem.innerHTML="Specify a 3' gene";
    exit();
  }

  if (!gene5primeloc) {
    var elem = document.getElementById("warningDiv");
    elem.style.visibility = "visible";
    elem.innerHTML="Specify a 5' gene fusion junction location";
    exit();
  } else if (!isInt(gene5primeloc)) {
    var elem = document.getElementById("warningDiv");
    elem.style.visibility = "visible";
    elem.innerHTML="The 5' gene fusion junction location should be an integer";
    exit();
  }

  if (!gene3primeloc) {
    var elem = document.getElementById("warningDiv");
    elem.style.visibility = "visible";
    elem.innerHTML="Specify a 3' gene fusion junction location";
    exit();
  } else if (!isInt(gene3primeloc)) {
    var elem = document.getElementById("warningDiv");
    elem.style.visibility = "visible";
    elem.innerHTML="The 3' gene fusion junction location should be an integer";
    exit();
  }

  var elem = document.getElementById("warningDiv");
  elem.style.visibility = "hidden";
}
