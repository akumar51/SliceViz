document.addEventListener("DOMContentLoaded", function() {
  // Create the navigation bar
  var navBar = document.createElement("nav");
  navBar.className = "navbar navbar-expand-lg navbar-dark bg-dark";

  var containerDiv = document.createElement("div");
  containerDiv.className = "container";

  var brandLink = document.createElement("a");
  brandLink.className = "navbar-brand";
  brandLink.href = "#";
  brandLink.textContent = "My Website";

  containerDiv.appendChild(brandLink);

  var navButton = document.createElement("button");
  navButton.className = "navbar-toggler";
  navButton.type = "button";
  navButton.setAttribute("data-toggle", "collapse");
  navButton.setAttribute("data-target", "#navbarNav");
  navButton.setAttribute("aria-controls", "navbarNav");
  navButton.setAttribute("aria-expanded", "false");
  navButton.setAttribute("aria-label", "Toggle navigation");

  var navButtonIcon = document.createElement("span");
  navButtonIcon.className = "navbar-toggler-icon";
  navButton.appendChild(navButtonIcon);

  containerDiv.appendChild(navButton);

  var collapseDiv = document.createElement("div");
  collapseDiv.className = "collapse navbar-collapse";
  collapseDiv.id = "navbarNav";

  var navList = document.createElement("ul");
  navList.className = "navbar-nav";

  var navItems = [
    { text: "Home", href: "#" },
    { text: "About", href: "#" },
    { text: "Services", href: "#" },
    { text: "Contact", href: "#" }
  ];

  navItems.forEach(function(item) {
    var listItem = document.createElement("li");
    listItem.className = "nav-item";

    var link = document.createElement("a");
    link.className = "nav-link";
    link.href = item.href;
    link.textContent = item.text;

    listItem.appendChild(link);
    navList.appendChild(listItem);
  });

  collapseDiv.appendChild(navList);
  containerDiv.appendChild(collapseDiv);
  navBar.appendChild(containerDiv);

  // Insert the navigation bar into the document
  var navbarContainer = document.getElementById("navbar-container");
  if (navbarContainer) {
    navbarContainer.appendChild(navBar);
  }
});
