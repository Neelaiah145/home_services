(function ($) {
  "use strict";


  /*=================================
      JS Index Here
  ==================================*/
  /*
    01. Preloader
    02. Mobile Menu Active
    03. Sticky fix
    04. Scroll To Top
    05. Set Background Image
    06. Global Slider
    07. Ajax Contact Form
    08. Magnific Popup
    09. Filter
    10. Popup Sidemenu   
    11. Counter section
    12. side cart toggle
    13. Search Box Popup
    14. Lenis Library Support
    15. Split Text Animation With GSAP Plugins
    16. Active Menu Item Based On URL
    17. Back to Top
    18. Nice Select
    19. package tab
    20. FIle Upload
    21. countdown timer
    22. Renge
    23. hero animate
  */
  /*=================================
      JS Index End
  ==================================*/
  /*

  /*---------- 01. Preloader ----------*/



  
$(window).on('load', function () {
  const preloader = $('.preloader');
  const preloaderCls = $('.preloaderCls');

  if (!preloader.length) return;

  // Function to hide preloader with GSAP
  const hidePreloader = () => {
    gsap.to(preloader, {
      y: '-100%',
      duration: 1.2,
      ease: 'power3.inOut',
      onComplete: () => preloader.hide(),
    });
  };

  // Run on window load
  hidePreloader();

  // Run on click if preloaderCls exists
  if (preloaderCls.length) {
    preloaderCls.on('click', function (e) {
      e.preventDefault();
      hidePreloader();
    });
  }
});


    /**************************************
   ***** 15. WoW Js Animation *****
   **************************************/
   let wow = new WOW({
    boxClass: "wow",
    animateClass: "wow-animated",
    offset: 0,
    mobile: false,
    live: true,
    scrollContainer: null,
    resetAnimation: false,
  });
  wow.init();

// hero-img 
  // gsap.from(".hero-img img", {
  //   opacity: 0,
  //   scale: 1.4,
  //   y: 60,
  //   rotation: 5,
  //   duration: 1.8,
  //   ease: "power4.out"
  // });

  // });

  /*---------- 02. Mobile Menu Active ----------*/
  $.fn.vsmobilemenu = function (options) {
    var opt = $.extend({
        menuToggleBtn: ".vs-menu-toggle",
        bodyToggleClass: "vs-body-visible",
        subMenuClass: "vs-submenu",
        subMenuParent: "vs-item-has-children",
        subMenuParentToggle: "vs-active",
        meanExpandClass: "vs-mean-expand",
        appendElement: '<span class="vs-mean-expand"></span>',
        subMenuToggleClass: "vs-open",
        toggleSpeed: 400,
      },
      options
    );

    return this.each(function () {
      var menu = $(this); // Select menu

      // Menu Show & Hide
      function menuToggle() {
        menu.toggleClass(opt.bodyToggleClass);

        // collapse submenu on menu hide or show
        var subMenu = "." + opt.subMenuClass;
        $(subMenu).each(function () {
          if ($(this).hasClass(opt.subMenuToggleClass)) {
            $(this).removeClass(opt.subMenuToggleClass);
            $(this).css("display", "none");
            $(this).parent().removeClass(opt.subMenuParentToggle);
          }
        });
      }

      // Class Set Up for every submenu
      menu.find("li").each(function () {
        var submenu = $(this).find("ul");
        submenu.addClass(opt.subMenuClass);
        submenu.css("display", "none");
        submenu.parent().addClass(opt.subMenuParent);
        submenu.prev("a").append(opt.appendElement);
        submenu.next("a").append(opt.appendElement);
      });

      // Toggle Submenu
      function toggleDropDown($element) {
        if ($($element).next("ul").length > 0) {
          $($element).parent().toggleClass(opt.subMenuParentToggle);
          $($element).next("ul").slideToggle(opt.toggleSpeed);
          $($element).next("ul").toggleClass(opt.subMenuToggleClass);
        } else if ($($element).prev("ul").length > 0) {
          $($element).parent().toggleClass(opt.subMenuParentToggle);
          $($element).prev("ul").slideToggle(opt.toggleSpeed);
          $($element).prev("ul").toggleClass(opt.subMenuToggleClass);
        }
      }

      // Submenu toggle Button
      var expandToggler = "." + opt.meanExpandClass;
      $(expandToggler).each(function () {
        $(this).on("click", function (e) {
          e.preventDefault();
          toggleDropDown($(this).parent());
        });
      });

      // Menu Show & Hide On Toggle Btn click
      $(opt.menuToggleBtn).each(function () {
        $(this).on("click", function () {
          menuToggle();
        });
      });

      // Hide Menu On out side click
      menu.on("click", function (e) {
        e.stopPropagation();
        menuToggle();
      });

      // Stop Hide full menu on menu click
      menu.find("div").on("click", function (e) {
        e.stopPropagation();
      });
    });
  };

  $(".vs-menu-wrapper").vsmobilemenu();

  /*---------- 03. Header  Start ----------*/
  $("ul>li>.submenu").parent("li").addClass("menu-item-has-children");
  // drop down menu width overflow problem fix
  $('ul').parent('li').on('hover', function () {
      var menu = $(this).find("ul");
      var menupos = $(menu).offset();
      if (menupos.left + menu.width() > $(window).width()) {
          var newpos = -$(menu).width();
          menu.css({
              left: newpos
          });
      }
  });

  $('.menu li a').on('click', function (e) {
      var element = $(this).parent('li');
      if (element.hasClass('open')) {
          element.removeClass('open');
          element.find('li').removeClass('open');
          element.find('ul').slideUp(300, "swing");
      } else {
          element.addClass('open');
          element.children('ul').slideDown(300, "swing");
          element.siblings('li').children('ul').slideUp(300, "swing");
          element.siblings('li').removeClass('open');
          element.siblings('li').find('li').removeClass('open');
          element.siblings('li').find('ul').slideUp(300, "swing");
      }
  })
  $('.ellepsis-bar').on('click', function (e) {
      var element = $('.header-top');
      if (element.hasClass('open')) {
          element.removeClass('open');
          element.slideUp(300, "swing");
          $('.overlayTwo').removeClass('active');
      } else {
          element.addClass('open');
          element.slideDown(300, "swing");
          $('.overlayTwo').addClass('active');
      }
  });
  $('.header-bar').on('click', function () {
      $(this).toggleClass('active');
      $('.menu').toggleClass('active');
  })


/*---------- 04. Sticky fix ----------*/
let lastScrollTop = 0;
const scrollToTopBtn = ".scrollToTop";

function stickyMenu($targetMenu, $toggleClass, $parentClass) {
  let st = $(window).scrollTop();
  let height = $targetMenu.outerHeight();

  $targetMenu.parent().css("min-height", height);

  if (st > 0) {
    $targetMenu.parent().addClass($parentClass);
    $targetMenu.addClass($toggleClass);
  } else {
    $targetMenu.parent().removeClass($parentClass);
    $targetMenu.removeClass($toggleClass);
  }
}

$(window).on("scroll", function () {
  stickyMenu($(".sticky-active"), "active", "will-sticky");
  if ($(this).scrollTop() > 500) {
    $(scrollToTopBtn).addClass("show");
  } else {
    $(scrollToTopBtn).removeClass("show");
  }
});

/*---------- 05. Scroll To Top (Smooth + Fallback) ----------*/
$(scrollToTopBtn).on("click", function (e) {
  e.preventDefault();
  if (typeof lenis !== "undefined") {
    lenis.scrollTo(0, { duration: 1.4 });
  } else {
    $("html, body").animate({ scrollTop: 0 }, 600);
  }
});




  /*---------- 06. Set Background Image ----------*/
  if ($("[data-bg-src]").length > 0) {
    $("[data-bg-src]").each(function () {
      var src = $(this).attr("data-bg-src");
      $(this).css("background-image", "url(" + src + ")");
      $(this).removeAttr("data-bg-src").addClass("background-image");
    });
  }

  /*----------- 07. Global Slider ----------*/
  $(".vs-carousel").each(function () {
    var asSlide = $(this);

    // Collect Data
    function d(data) {
      return asSlide.data(data);
    }

    // Custom Arrow Button
    var prevButton =
      '<button type="button" class="slick-prev"><i class="' +
      d("prev-arrow") +
      '"></i></button>',
      nextButton =
      '<button type="button" class="slick-next"><i class="' +
      d("next-arrow") +
      '"></i></button>';

    // Function For Custom Arrow Btn
    $("[data-slick-next]").each(function () {
      $(this).on("click", function (e) {
        e.preventDefault();
        $($(this).data("slick-next")).slick("slickNext");
      });
    });

    $("[data-slick-prev]").each(function () {
      $(this).on("click", function (e) {
        e.preventDefault();
        $($(this).data("slick-prev")).slick("slickPrev");
      });
    });

    // Check for arrow wrapper
    if (d("arrows") == true) {
      if (!asSlide.closest(".arrow-wrap").length) {
        asSlide.closest(".container").parent().addClass("arrow-wrap");
      }
    }

    asSlide.slick({
      dots: d("dots") ? true : false,
      fade: d("fade") ? true : false,
      arrows: d("arrows") ? true : false,
      speed: d("speed") ? d("speed") : 1000,
      asNavFor: d("asnavfor") ? d("asnavfor") : false,
      autoplay: d("autoplay") == true ? true : false,
      infinite: d("infinite") == false ? false : true,
      slidesToShow: d("slide-show") ? d("slide-show") : 1,
      adaptiveHeight: d("adaptive-height") ? true : false,
      centerMode: d("center-mode") ? true : false,
      autoplaySpeed: d("autoplay-speed") ? d("autoplay-speed") : 8000,
      centerPadding: d("center-padding") ? d("center-padding") : "0",
      focusOnSelect: d("focuson-select") == false ? false : true,
      pauseOnFocus: d("pauseon-focus") ? true : false,
      pauseOnHover: d("pauseon-hover") ? true : false,
      variableWidth: d("variable-width") ? true : false,
      vertical: d("vertical") ? true : false,
      verticalSwiping: d("vertical") ? true : false,
      prevArrow: d("prev-arrow") ?
        prevButton : '<button type="button" class="slick-prev"><i class="fa-solid fa-arrow-left"></i></button>',
      nextArrow: d("next-arrow") ?
        nextButton : '<button type="button" class="slick-next"><i class="fa-solid fa-arrow-right"></i></button>',
      rtl: $("html").attr("dir") == "rtl" ? true : false,
      responsive: [{
          breakpoint: 1600,
          settings: {
            arrows: d("xl-arrows") ? true : false,
            dots: d("xl-dots") ? true : false,
            slidesToShow: d("xl-slide-show") ?
              d("xl-slide-show") : d("slide-show"),
            centerMode: d("xl-center-mode") ? true : false,
            centerPadding: 0,
          },
        },
        {
          breakpoint: 1400,
          settings: {
            arrows: d("ml-arrows") ? true : false,
            dots: d("ml-dots") ? true : false,
            slidesToShow: d("ml-slide-show") ?
              d("ml-slide-show") : d("slide-show"),
            centerMode: d("ml-center-mode") ? true : false,
            centerPadding: 0,
          },
        },
        {
          breakpoint: 1200,
          settings: {
            arrows: d("lg-arrows") ? true : false,
            dots: d("lg-dots") ? true : false,
            // vertical:d("lg-vertical") ? true : false,
            slidesToShow: d("lg-slide-show") ?
              d("lg-slide-show") : d("slide-show"),
            centerMode: d("lg-center-mode") ? d("lg-center-mode") : false,
            centerPadding: 0,
          },
        },
        {
          breakpoint: 992,
          settings: {
            arrows: d("md-arrows") ? true : false,
            dots: d("md-dots") ? true : false,
            vertical:d("md-vertical") ? true : false,
            slidesToShow: d("md-slide-show") ? d("md-slide-show") : 1,
            centerMode: d("md-center-mode") ? d("md-center-mode") : false,
            centerPadding: 0,
          },
        },
        {
          breakpoint: 767,
          settings: {
            arrows: d("sm-arrows") ? true : false,
            dots: d("sm-dots") ? true : false,
            vertical:d("sm-vertical") ? true : false,
            slidesToShow: d("sm-slide-show") ? d("sm-slide-show") : 1,
            centerMode: d("sm-center-mode") ? d("sm-center-mode") : false,
            centerPadding: 0,
          },
        },
        {
          breakpoint: 576,
          settings: {
            arrows: d("xs-arrows") ? true : false,
            dots: d("xs-dots") ? true : false,
            vertical:d("xs-vertical") ? true : false,
            slidesToShow: d("xs-slide-show") ? d("xs-slide-show") : 1,
            centerMode: d("xs-center-mode") ? d("xs-center-mode") : false,
            centerPadding: 0,
          },
        },
        // You can unslick at a given breakpoint now by adding:
        // settings: "unslick"
        // instead of a settings object
      ],
    });


  });

  /*----------- 08. Ajax Contact Form ----------*/
  var form = ".ajax-contact";
  var invalidCls = "is-invalid";
  var $email = '[name="email"]';
  var $validation =
    '[name="name"],[name="email"],[name="subject"],[name="message"]'; // Must be use (,) without any space
  var formMessages = $(".form-messages");

  function sendContact() {
    var formData = $(form).serialize();
    var valid;
    valid = validateContact();
    if (valid) {
      jQuery
        .ajax({
          url: $(form).attr("action"),
          data: formData,
          type: "POST",
        })
        .done(function (response) {
          // Make sure that the formMessages div has the 'success' class.
          formMessages.removeClass("error");
          formMessages.addClass("success");
          // Set the message text.
          formMessages.text(response);
          // Clear the form.
          $(form + ' input:not([type="submit"]),' + form + " textarea").val("");
        })
        .fail(function (data) {
          // Make sure that the formMessages div has the 'error' class.
          formMessages.removeClass("success");
          formMessages.addClass("error");
          // Set the message text.
          if (data.responseText !== "") {
            formMessages.html(data.responseText);
          } else {
            formMessages.html(
              "Oops! An error occured and your message could not be sent."
            );
          }
        });
    }
  }

  function validateContact() {
    var valid = true;
    var formInput;

    function unvalid($validation) {
      $validation = $validation.split(",");
      for (var i = 0; i < $validation.length; i++) {
        formInput = form + " " + $validation[i];
        if (!$(formInput).val()) {
          $(formInput).addClass(invalidCls);
          valid = false;
        } else {
          $(formInput).removeClass(invalidCls);
          valid = true;
        }
      }
    }
    unvalid($validation);

    if (
      !$($email).val() ||
      !$($email)
      .val()
      .match(/^([\w-\.]+@([\w-]+\.)+[\w-]{2,4})?$/)
    ) {
      $($email).addClass(invalidCls);
      valid = false;
    } else {
      $($email).removeClass(invalidCls);
      valid = true;
    }
    return valid;
  }

  $(form).on("submit", function (element) {
    element.preventDefault();
    sendContact();
  });

  /*----------- 09. Magnific Popup ----------*/
  /* magnificPopup img view */
  $(".popup-image").magnificPopup({
    type: "image",
    gallery: {
      enabled: true,
    },
  });

  /* magnificPopup video view */
  $(".popup-video").magnificPopup({
    type: "iframe",
  });

  /*----------- 10. Filter ----------*/
  $(".filter-active").imagesLoaded(function () {
    var $filter = ".filter-active",
      $filterItem = ".filter-item",
      $filterMenu = ".filter-menu-active";

    if ($($filter).length > 0) {
      var $grid = $($filter).isotope({
        itemSelector: $filterItem,
        filter: "*",
        masonry: {
          // use outer width of grid-sizer for columnWidth
          columnWidth: 1,
        },
      });

      // filter items on button click
      $($filterMenu).on("click", "div", function () {
        var filterValue = $(this).attr("data-filter");
        $grid.isotope({
          filter: filterValue,
        });
      });

      // Menu Active Class
      $($filterMenu).on("click", "div", function (event) {
        event.preventDefault();
        $(this).addClass("active");
        $(this).siblings(".active").removeClass("active");
      });
    }
  });



  /*---------- 10. Popup Sidemenu ----------*/
  function popupSideMenu($sideMenu, $sideMunuOpen, $sideMenuCls, $toggleCls) {
    // Sidebar Popup
    $($sideMunuOpen).on("click", function (e) {
      e.preventDefault();
      $($sideMenu).addClass($toggleCls);
    });
    $($sideMenu).on("click", function (e) {
      e.stopPropagation();
      $($sideMenu).removeClass($toggleCls);
    });
    var sideMenuChild = $sideMenu + " > div";
    $(sideMenuChild).on("click", function (e) {
      e.stopPropagation();
      $($sideMenu).addClass($toggleCls);
    });
    $($sideMenuCls).on("click", function (e) {
      e.preventDefault();
      e.stopPropagation();
      $($sideMenu).removeClass($toggleCls);
    });
  }
  popupSideMenu(
    ".sidemenu-wrapper",
    ".sideMenuToggler",
    ".sideMenuCls",
    "show"
  );

 /*----------- 11. Counter section ----------*/
 var a = 0;

  $(window).scroll(function () {
    var mediaCounter = $(".media-counter");

    if (mediaCounter.length > 0) {
      var oTop = mediaCounter.offset().top - window.innerHeight;

      if (a == 0 && $(window).scrollTop() > oTop) {
        $(".counter-number").each(function () {
          var $this = $(this),
            countTo = $this.attr("data-count");
          $({ countNum: $this.text() }).animate(
            {
              countNum: countTo,
            },
            {
              duration: 4000,
              easing: "swing",
              step: function () {
                $this.text(Math.floor(this.countNum));
              },
              complete: function () {
                $this.text(this.countNum);
                //alert('finished');
              },
            }
          );
        });
        a = 1;
      }
    }
  });

  /*----------- 12. side cart toggle----------*/
 
  // Event handler for the close button
  $(".sideMenuCls2").on("click", function() {
    $(".sideCart-wrapper").removeClass("show");
  });

  // Event handler for toggling the side cart when clicking outside the side cart wrapper
  $(".sideCart-wrapper").on("click", function(event) {
    if (!$(event.target).closest(".sidemenu-content").length) {
        toggleSideCart();
    }
  });

  // Event handler for the toggler button
  $(".sideCartToggler").on("click", function() {
    toggleSideCart();
  });

  // Function to toggle the side cart
  function toggleSideCart() {
    $(".sideCart-wrapper").toggleClass("show");
  }

   /*---------- 13. Search Box Popup ----------*/
   function popupSarchBox($searchBox, $searchOpen, $searchCls, $toggleCls) {
    $($searchOpen).on("click", function (e) {
      e.preventDefault();
      $($searchBox).addClass($toggleCls);
    });
    $($searchBox).on("click", function (e) {
      e.stopPropagation();
      $($searchBox).removeClass($toggleCls);
    });
    $($searchBox)
      .find("form")
      .on("click", function (e) {
        e.stopPropagation();
        $($searchBox).addClass($toggleCls);
      });
    $($searchCls).on("click", function (e) {
      e.preventDefault();
      e.stopPropagation();
      $($searchBox).removeClass($toggleCls);
    });
  }
  popupSarchBox(
    ".popup-search-box",
    ".searchBoxTggler",
    ".searchClose",
    "show"
  );


/*---------- 14. Lenis Library Support ----------*/
gsap.registerPlugin(ScrollTrigger, ScrollToPlugin, SplitText);




/* ----------------------------
   02. Lenis Smooth Scroll Setup + GSAP SplitText
---------------------------- */
document.addEventListener("DOMContentLoaded", () => {
  // ---------- 01. Lenis Smooth Scroll ----------
  if (typeof Lenis !== "undefined") {
    const lenis = new Lenis({
      lerp: 0.08,            // ছোট মান => smoother scroll
      smoothWheel: true,     // mouse wheel smooth
      smoothTouch: false,    // mobile touch disable
      autoResize: true,
      easing: (t) => 1 - Math.pow(2, -10 * t), // natural easing
    });

    // Sync Lenis with ScrollTrigger
    lenis.on("scroll", () => {
      if (typeof ScrollTrigger !== "undefined") ScrollTrigger.update();
    });

    // RAF loop
    gsap.ticker.add((time) => lenis.raf(time * 1000));
    gsap.ticker.lagSmoothing(0);
    window.lenis = lenis; // global access
  }

  // ---------- 02. SplitText Animation ----------
  function vsTitleAnimation() {
    const vsElements = document.querySelectorAll(".title-anime");
    if (!vsElements.length || typeof SplitText === "undefined") return;

    vsElements.forEach((container) => {
      const quotes = container.querySelectorAll(".title-anime__title");
      quotes.forEach((quote) => {
        // Clean previous animation
        if (quote.animation) {
          quote.animation.kill();
          if (quote.split) quote.split.revert();
        }

        // Apply SplitText
        quote.split = new SplitText(quote, {
          type: "lines,words,chars",
          linesClass: "split-line",
        });

        const chars = quote.split.chars;
        gsap.set(chars, { opacity: 0, y: "100%" });
        gsap.set(quote, { perspective: 1000 });

        // Animation
        quote.animation = gsap.to(chars, {
          y: "0%",
          opacity: 1,
          duration: 1,
          ease: "back.out(1.7)",
          stagger: 0.02,
          scrollTrigger: {
            trigger: quote,
            start: "top 90%",
            toggleActions: "play none none none",
          },
        });
      });
    });
  }

  // ---------- 03. ScrollTrigger refresh handlers ----------
  if (typeof ScrollTrigger !== "undefined") {
    ScrollTrigger.addEventListener("refreshInit", () => {
      document.querySelectorAll(".title-anime__title").forEach((quote) => {
        if (quote.split) quote.split.revert();
      });
    });
    ScrollTrigger.addEventListener("refresh", vsTitleAnimation);
  }

  // Initial call
  vsTitleAnimation();
});


  /*---------- 16. Active Menu Item Based On URL ----------*/
  document.addEventListener('DOMContentLoaded', () => {
    const navMenu = document.querySelector('.main-menu'); // Select the main menu container once
    const windowPathname = window.location.pathname;

    if (navMenu) {
      const navLinkEls = navMenu.querySelectorAll('a'); // Only get <a> tags inside the main menu

      navLinkEls.forEach((navLinkEl) => {
        const navLinkPathname = new URL(navLinkEl.href, window.location.origin)
          .pathname;

        // Match current URL with link's href
        if (
          windowPathname === navLinkPathname ||
          (windowPathname === '/index.html' && navLinkPathname === '/')
        ) {
          navLinkEl.classList.add('active');

          // Add 'active' class to all parent <li> elements
          let parentLi = navLinkEl.closest('li');
          while (parentLi && parentLi !== navMenu) {
            parentLi.classList.add('active');
            parentLi = parentLi.parentElement.closest('li'); // Traverse up safely
          }
        }
      });
    }
  });

   /*----------- 17. Back to Top ----------*/
  // Get references to DOM elements
  const backToTopBtn = document.getElementById('backToTop');
  const progressCircle = document.querySelector('.progress');
  const progressPercentage = document.getElementById('progressPercentage');

 if (backToTopBtn && progressCircle && progressPercentage) {
  const CIRCLE_RADIUS = 40;
  const CIRCUMFERENCE = 2 * Math.PI * CIRCLE_RADIUS;
  progressCircle.style.strokeDasharray = CIRCUMFERENCE;
  progressCircle.style.strokeDashoffset = CIRCUMFERENCE;

  const updateProgress = () => {
    const scrollPosition = window.scrollY;
    const totalHeight = document.documentElement.scrollHeight - window.innerHeight;
    if (totalHeight <= 0) return;
    const scrollPercentage = (scrollPosition / totalHeight) * 100;
    const offset = CIRCUMFERENCE * (1 - scrollPercentage / 100);
    progressCircle.style.strokeDashoffset = offset.toFixed(2);
    progressPercentage.textContent = `${Math.round(scrollPercentage)}%`;
  };

  const scrollToTop = () => {
    if (gsap && gsap.to) gsap.to(window, { duration: 1, scrollTo: 0 });
    else window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const throttle = (func, limit) => {
    let lastFunc, lastRan;
    return function (...args) {
      const context = this;
      if (!lastRan) {
        func.apply(context, args);
        lastRan = Date.now();
      } else {
        clearTimeout(lastFunc);
        lastFunc = setTimeout(() => {
          if (Date.now() - lastRan >= limit) {
            func.apply(context, args);
            lastRan = Date.now();
          }
        }, limit - (Date.now() - lastRan));
      }
    };
  };

  window.addEventListener('scroll', throttle(updateProgress, 50));
  backToTopBtn.addEventListener('click', scrollToTop);
  updateProgress();
}



 /*----------- 18. Nice Select ----------*/
 if ($("select").length > 0) {
  $("select").niceSelect();
}

gsap.registerPlugin(ScrollTrigger);


/*----------- 19. Package Tabs ----------*/
(function packageTabs() {
  const tabs = document.querySelectorAll('[data-tab-target]');
  const tabContents = document.querySelectorAll('[data-tab-content]');
  if (!tabs.length || !tabContents.length) return;

  tabs.forEach(tab => {
    tab.addEventListener('click', () => {
      const targetSelector = tab.dataset.tabTarget;
      const target = document.querySelector(targetSelector);
      if (!target) return; // safety check

      // Remove active from all
      tabContents.forEach(tc => tc.classList.remove('active'));
      tabs.forEach(t => t.classList.remove('active'));

      // Activate clicked tab and target content
      tab.classList.add('active');
      target.classList.add('active');
    });
  });
})();


/*----------- 20. File Upload ----------*/
$(".file-upload").each(function () {
  const fI = $(this).children('input[type="file"]'),
        btn = $(this).children('.btn-upload'),
        i1  = $(this).children('.i-pic-upload'),
        i2  = $(this).children('.i-deselect'),
        tfN = $(this).find('.text-file-name'),
        bT  = $(this).find('.text-browse');

  const defaultText = "No file Selected";
  const browseText  = "Browse...";
  const changeText  = "Change...";

  // Initial state
  bT.text(browseText);
  tfN.text(defaultText);

  // Browse button → trigger file input
  btn.on("click", function (e) {
    e.preventDefault();
    fI.trigger("click");
  });

  // File preview
  function readURL(input) {
    if (input.files && input.files[0]) {
      const reader = new FileReader();
      reader.onload = function (e) {
        i1.css({
          "background": `url(${e.target.result}) no-repeat center`,
          "background-size": "cover"
        }).removeClass("fa fa-camera");
      };
      reader.readAsDataURL(input.files[0]);
    }
  }

  // On file select
  fI.on("change", function (e) {
    if (e.target.files[0]) {
      readURL(this);
      tfN.text(e.target.files[0].name);
      i2.fadeIn(200);
      bT.text(changeText);
    }
  });

  // On deselect/reset
  i2.on("click", function () {
    i2.fadeOut(100);
    setTimeout(function () {
      i1.css("background", "#ebebeb").addClass("fa fa-camera");
      bT.text(browseText);
      tfN.text(defaultText);
      fI.val(null); // reset input
    }, 200);
  });
});


/*----------- 21. Countdown Timer ----------*/
function initCountdown() {
  $(".offer-counter").each(function () {
    const $this = $(this);
    const offerDateStr = $this.attr("data-offer-date");
    const offerDate = new Date(offerDateStr);

    function updateCountdown() {
      const now = new Date();
      let timeDiff = offerDate.getTime() - now.getTime();

      if (timeDiff <= 0) {
        // Countdown expired → set 0s
        $this.find(".day").text("00");
        $this.find(".hour").text("00");
        $this.find(".minute").text("00");
        $this.find(".second").text("00");
        return;
      }

      const days = Math.floor(timeDiff / (1000 * 60 * 60 * 24));
      const hours = Math.floor((timeDiff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
      const minutes = Math.floor((timeDiff % (1000 * 60 * 60)) / (1000 * 60));
      const seconds = Math.floor((timeDiff % (1000 * 60)) / 1000);

      $this.find(".day").text(days.toString().padStart(2, "0"));
      $this.find(".hour").text(hours.toString().padStart(2, "0"));
      $this.find(".minute").text(minutes.toString().padStart(2, "0"));
      $this.find(".second").text(seconds.toString().padStart(2, "0"));
    }

    // Initial + Interval
    updateCountdown();
    setInterval(updateCountdown, 1000);
  });
}

// Initialize countdowns
initCountdown();


/*----------- 22. Range Slider ----------*/
const slider = document.getElementById("range-slider__range");
const output = document.getElementById("range-slider__value");

if (slider && output) {
  function updateSlider() {
    const min = Number(slider.min) || 0;
    const max = Number(slider.max) || 100;
    const value = Number(slider.value);

    output.textContent = value;

    const valuePercent = ((value - min) / (max - min)) * 100;
    slider.style.background = `linear-gradient(to right, #F86E2D 0%, #F86E2D ${valuePercent}%, #d7dcdf ${valuePercent}%, #d7dcdf 100%)`;
  }

  // Run once on load
  updateSlider();

  // Event listener
  slider.addEventListener("input", updateSlider);
}

/*----------- 23. hero animate ----------*/
window.addEventListener("load", function () {
  let hero = document.querySelector(".vs-hero");
  let image = hero ? hero.querySelector(".hero-item") : null;

  if (hero && image) {
    gsap.set(hero, { autoAlpha: 1 });
    let tl = gsap.timeline();
    tl.from(hero, {
      duration: 1,
      yPercent: -20,
      opacity: 0,
      ease: "power2.out"
    });
    tl.from(image, {
      duration: 1,
      yPercent: 20,
      scale: 1.1,
      opacity: 0,
      ease: "power2.out"
    }, "-=0.8");
  }
});

})(jQuery);



$('.hero-prev').click(function(){
  $('.hero-slider1').slick('slickPrev');
});

$('.hero-next').click(function(){
  $('.hero-slider1').slick('slickNext');
});

document.querySelector('input[name="image"]').addEventListener('change', function(e) {
    const file = e.target.files[0];
    const preview = document.getElementById('previewImg');

    if (file) {
        preview.src = URL.createObjectURL(file);
        preview.style.display = 'block';
    }
});


//  categories services 
  const categorySelect = document.getElementById('category-select');
  const serviceSelect = document.getElementById('service-select');

  categorySelect.addEventListener('change', function () {
    const categoryId = this.value;

    // Reset services
    serviceSelect.innerHTML = '<option value="">-- select service --</option>';

    if (!categoryId) return;

    fetch(`/api/category/${categoryId}/services/`)
      .then(res => res.json())
      .then(data => {
        data.services.forEach(service => {
          const option = document.createElement('option');
          option.value = service.id;
          option.textContent = service.s_title;
          serviceSelect.appendChild(option);
        });
      })
      .catch(err => console.error('Failed to load services:', err));
  });

