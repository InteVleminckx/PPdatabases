const menu = document.querySelector("#mobile-menu");
const menuLinks = document.querySelector(".navbar_menu")


// Display Mobile Menu
const mobileMenu = () => {
    menu.classList.toggle('is-active');
    menuLinks.classList.toggle('active');
}

menu.addEventListener('click', mobileMenu);

const highlightMenu = () => {

    const elem = document.querySelector(".highlight")
    const homeMenu = document.querySelector("#home-page")
    const aboutMenu = document.querySelector("#about-page")
    const servicesMenu = document.querySelector("#services-page")
    const contactMenu = document.querySelector("#contact-page")

    let scrollPos = this.scrollY;
    console.log(scrollPos)

    let home = [488,1417]
    let services = [1417,2346]
    let about = [2346,3046]
    let contact = 3046

    if (window.innerWidth > 1100 && scrollPos >= home[0] && scrollPos < home[1]){
        homeMenu.classList.add('highlight')
        servicesMenu.classList.remove('highlight')
        return;
    }
    
    else if (window.innerWidth > 1100 && scrollPos >= services[0] && scrollPos < services[1]){
        homeMenu.classList.remove('highlight')
        servicesMenu.classList.add('highlight')
        aboutMenu.classList.remove('highlight')
        return;
    }

    else if (window.innerWidth > 1100 && scrollPos >= about[0] && scrollPos < about[1]){
        servicesMenu.classList.remove('highlight')
        aboutMenu.classList.add('highlight')
        contactMenu.classList.remove('highlight')
        return;
    }

    else if (window.innerWidth > 1100 && scrollPos >= contact){
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





