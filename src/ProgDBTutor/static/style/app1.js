const menu = document.querySelector("#mobile-menu");
const menuLinks = document.querySelector(".navbar_menu")


// Display Mobile Menu
const mobileMenu = () => {
    menu.classList.toggle('is-active');
    menuLinks.classList.toggle('active');

    const homeMenu = document.querySelector("#home-page")
    const aboutMenu = document.querySelector("#about-page")
    const servicesMenu = document.querySelector("#services-page")
    const contactMenu = document.querySelector("#contact-page")

    homeMenu.classList.remove('highlight')
    servicesMenu.classList.remove('highlight')
    aboutMenu.classList.remove('highlight')
    contactMenu.classList.remove('highlight')

}

menu.addEventListener('click', mobileMenu);

const highlightMenu = () => {

    const elem = document.querySelector(".highlight")
    const homeMenu = document.querySelector("#home-page")
    const aboutMenu = document.querySelector("#about-page")
    const servicesMenu = document.querySelector("#services-page")
    const contactMenu = document.querySelector("#contact-page")

    const headerHeight = document.querySelector("#header").offsetHeight
    const navbarHeight = document.querySelector("#navbar").offsetHeight
    const homeHeight = document.querySelector("#home").offsetHeight + headerHeight + navbarHeight
    const servicesHeight = document.querySelector("#services").offsetHeight + homeHeight
    const aboutHeight = document.querySelector("#about").offsetHeight + servicesHeight
    const contactHeight = document.querySelector("#contact").offsetHeight
    const footerHeight = document.querySelector("#footer").offsetHeight

    let scrollPos = this.scrollY;

    console.log(scrollPos + " " + homeHeight + " " + servicesHeight + " " + aboutHeight + " " + contactHeight + " " + footerHeight + " " + (aboutHeight - contactHeight - footerHeight))


    if (window.innerWidth > 1100 && scrollPos < homeHeight){
        homeMenu.classList.add('highlight')
        servicesMenu.classList.remove('highlight')
        return;
    }

    else if (window.innerWidth > 1100 && scrollPos < servicesHeight){
        homeMenu.classList.remove('highlight')
        servicesMenu.classList.add('highlight')
        aboutMenu.classList.remove('highlight')
        return;
    }

    else if (window.innerWidth > 1100 && scrollPos < (aboutHeight - contactHeight - footerHeight)){
        servicesMenu.classList.remove('highlight')
        aboutMenu.classList.add('highlight')
        contactMenu.classList.remove('highlight')
        return;
    }

    else if (window.innerWidth > 1100 && scrollPos >= (aboutHeight - contactHeight - footerHeight) ){
        aboutMenu.classList.remove('highlight')
        contactMenu.classList.add('highlight')
        return;
    }




}


// Close mobile Menu when clicking on a menu item

const hideMobileMenu = () => {
    const menuBars = document.querySelector('.is-active');
    let scroll = this.scrollY;
    if (window.innerWidth <= 1100 && menuBars && scroll >= 488){
        menu.classList.toggle('is-active')
        menuLinks.classList.remove('active')
    }

}

// window.addEventListener("scroll", (event) =>{
//     let scroll = this.scrollY;
//     console.log(scroll)
// })

window.addEventListener("scroll", highlightMenu);
window.addEventListener("click", highlightMenu);

menuLinks.addEventListener('click', hideMobileMenu)
window.addEventListener("scroll",hideMobileMenu)





