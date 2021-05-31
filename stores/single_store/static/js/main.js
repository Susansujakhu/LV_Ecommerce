(function ($) {
    "use strict";

    let passiveSupported = false;

    try {
        const options = Object.defineProperty({}, 'passive', {
            get: function() {
                passiveSupported = true;
            }
        });

        window.addEventListener('test', null, options);
    } catch(err) {}

    let DIRECTION = null;

    function direction() {
        if (DIRECTION === null) {
            DIRECTION = getComputedStyle(document.body).direction;
        }

        return DIRECTION;
    }

    function isRTL() {
        return direction() === 'rtl';
    }

    /*
    // initialize custom numbers
    */
    $(function () {
        $('.input-number').customNumber();
    });


    /*
    // product tabs
    */
    $(function () {
        $('.product-tabs').each(function (i, element) {
            const list = $('.product-tabs-list', element);

            list.on('click', '.product-tabs-item', function (event) {
                event.preventDefault();

                const tab = $(this);
                const pane = $('.product-tabs-pane' + $(this).attr('href'), element);

                if ($(element).is('.product-tabs--stuck')) {
                    window.scrollTo(0, $(element).find('.product-tabs-content').offset().top - $(element).find('.product-tabs-list-body').outerHeight() + 2);
                }

                if (pane.length) {
                    $('.product-tabs-item').removeClass('product-tabs-item--active');
                    tab.addClass('product-tabs-item--active');

                    $('.product-tabs-pane').removeClass('product-tabs-pane--active');
                    pane.addClass('product-tabs-pane--active');
                }
            });

            const currentTab = $('.product-tabs-item--active', element);
            const firstTab = $('.product-tabs-item:first', element);

            if (currentTab.length) {
                currentTab.trigger('click');
            } else {
                firstTab.trigger('click');
            }

            if ($(element).is('.product-tabs--sticky')) {
                let stuckWhen = null;
                let fixedWhen = null;

                function calc() {
                    stuckWhen = list.offset().top + list.outerHeight();
                    fixedWhen = $(element).find('.product-tabs-content').offset().top - $(element).find('.product-tabs-list-body').outerHeight() + 2;
                }

                function onScroll() {
                    if (stuckWhen === null || fixedWhen === null) {
                        calc();
                    }

                    if ( window.pageYOffset >= stuckWhen ) {
                        $(element).addClass('product-tabs--stuck');
                    } else if (window.pageYOffset < fixedWhen) {
                        $(element).removeClass('product-tabs--stuck');
                        $(element).removeClass('product-tabs--header-stuck-hidden');
                    }
                }

                window.addEventListener('scroll', onScroll, passiveSupported ? {passive: true} : false);

                $(document).on('stroyka.header.sticky.show', function(){
                    $(element).addClass('product-tabs--header-stuck');
                    $(element).removeClass('product-tabs--header-stuck-hidden');
                });
                $(document).on('stroyka.header.sticky.hide', function(){
                    $(element).removeClass('product-tabs--header-stuck');

                    if ($(element).is('.product-tabs--stuck')) {
                        $(element).addClass('product-tabs--header-stuck-hidden');
                    }
                });
                $(window).on('resize', function() {
                    stuckWhen = null;
                    fixedWhen = null;
                });

                onScroll();
            }
        });
    });


    /*
    // block slideshow
    */
    $(function() {
        $('.block-slideshow .owl-carousel').owlCarousel({
            items: 1,
            nav: false,
            dots: true,
            loop: false,
            rtl: isRTL()
        });
    });


    /*
    // block brands carousel
    */
    $(function() {
        $('.block-brands-slider .owl-carousel').owlCarousel({
            nav: false,
            dots: false,
            loop: false,
            rtl: isRTL(),
            responsive: {
                1200: {items: 6},
                992: {items: 5},
                768: {items: 4},
                576: {items: 3},
                0: {items: 2}
            }
        });
    });


    /*
    // block posts carousel
    */
    $(function() {
        $('.block-posts').each(function() {
            const layout = $(this).data('layout');
            const options = {
                margin: 30,
                nav: false,
                dots: false,
                loop: false,
                rtl: isRTL()
            };
            const layoutOptions = {
                'grid-3': {
                    responsive: {
                        992: {items: 3},
                        768: {items: 2},
                    }
                },
                'grid-4': {
                    responsive: {
                        1200: {items: 4, margin: 20},
                        992:  {items: 3, margin: 24},
                        768:  {items: 2, margin: 20},
                        460:  {items: 2, margin: 20},
                    }
                },
                'list': {
                    responsive: {
                        992: {items: 2},
                        0:   {items: 1},
                    }
                }
            };
            const owl = $('.block-posts-slider .owl-carousel');
            const owlOptions = $.extend({}, options, layoutOptions[layout]);

            if (/^grid-/.test(layout)) {
                let mobileResponsiveOptions = {};

                if (parseFloat($(this).data('mobile-columns')) === 2) {
                    mobileResponsiveOptions = {
                        460:  {items: 2, margin: 20},
                        400:  {items: 2, margin: 16},
                        320:  {items: 2, margin: 12},
                    };
                } else {
                    mobileResponsiveOptions = {
                        0: {items: 1},
                    };
                }

                owlOptions.responsive = $.extend({}, owlOptions.responsive, mobileResponsiveOptions);
            }

            owl.owlCarousel(owlOptions);

            $(this).find('.block-header-arrow--left').on('click', function() {
                owl.trigger('prev.owl.carousel', [500]);
            });
            $(this).find('.block-header-arrow--right').on('click', function() {
                owl.trigger('next.owl.carousel', [500]);
            });
        });
    });


    /*
    // teammates
    */
    $(function() {
        $('.teammates .owl-carousel').owlCarousel({
            nav: false,
            dots: true,
            rtl: isRTL(),
            responsive: {
                768: {items: 3, margin: 32},
                380: {items: 2, margin: 24},
                0: {items: 1}
            }
        });
    });

    /*
    // quickview
    */
    const quickview = {
        cancelPreviousModal: function() {},
        clickHandler: function() {
            const modal = $('#quickview-modal');
            const button = $(this);
            const doubleClick = button.is('.product-card-quickview--preload');

            quickview.cancelPreviousModal();

            if (doubleClick) {
                return;
            }

            button.addClass('product-card-quickview--preload');
       
            let xhr = $.ajax({
                    url: 'quick-view-modal-block.html',
                    success: function(data) {
                        quickview.cancelPreviousModal = function() {};
                        button.removeClass('product-card-quickview--preload');

                        modal.find('.modal-content').html(data);
                        modal.find('.quickview-close').on('click', function() {
                            modal.modal('hide');
                        });
                        modal.modal('show');
                    }
                });

            quickview.cancelPreviousModal = function() {
                button.removeClass('product-card-quickview--preload');

                if (xhr) {
                    xhr.abort();
                }
            };
        }
    };

    $(function () {
        const modal = $('#quickview-modal');

        modal.on('shown.bs.modal', function() {
            modal.find('.product').each(function () {
                const gallery = $(this).find('.product-gallery');

                if (gallery.length > 0) {
                    initProductGallery(gallery[0], $(this).data('layout'));
                }
            });

            $('.input-number', modal).customNumber();
        });

        $('.product-card-quickview').on('click', function() {
            quickview.clickHandler.apply(this, arguments);
        });
    });


    /*
    // products carousel
    */
    $(function() {
        $('.block-products-carousel').each(function() {
            const layout = $(this).data('layout');
            const options = {
                items: 4,
                margin: 14,
                nav: false,
                dots: false,
                loop: false,
                stagePadding: 1,
                rtl: isRTL()
            };
            const layoutOptions = {
                'grid-4': {
                    responsive: {
                        1200: {items: 4, margin: 14},
                        992:  {items: 4, margin: 10},
                        768:  {items: 3, margin: 10},
                    }
                },
                'grid-4-sm': {
                    responsive: {
                        1200: {items: 4, margin: 14},
                        992:  {items: 3, margin: 10},
                        768:  {items: 3, margin: 10},
                    }
                },
                'grid-5': {
                    responsive: {
                        1200: {items: 5, margin: 12},
                        992:  {items: 4, margin: 10},
                        768:  {items: 3, margin: 10},
                    }
                },
                'horizontal': {
                    items: 3,
                    slideBy: 'page',
                    responsive: {
                        1200: {items: 3, margin: 14},
                        992:  {items: 3, margin: 10},
                        768:  {items: 2, margin: 10},
                        576:  {items: 1},
                        475:  {items: 1},
                        0:    {items: 1}
                    }
                },
            };
            const owl = $('.owl-carousel', this);
            let cancelPreviousTabChange = function() {};

            const owlOptions = $.extend({}, options, layoutOptions[layout]);

            if (/^grid-/.test(layout)) {
                let mobileResponsiveOptions;

                if (parseFloat($(this).data('mobile-grid-columns')) === 2) {
                    mobileResponsiveOptions = {
                        420:  {items: 2, margin: 10},
                        320:  {items: 2, margin: 0},
                        0:    {items: 1},
                    };
                } else {
                    mobileResponsiveOptions = {
                        475:  {items: 2, margin: 10},
                        0:    {items: 1},
                    };
                }

                owlOptions.responsive = $.extend({}, owlOptions.responsive, mobileResponsiveOptions);
            }

            owl.owlCarousel(owlOptions);

            $(this).find('.block-header-arrow--left').on('click', function() {
                owl.trigger('prev.owl.carousel', [500]);
            });
            $(this).find('.block-header-arrow--right').on('click', function() {
                owl.trigger('next.owl.carousel', [500]);
            });
        });
    });


    /*
    // product gallery
    */
    const initProductGallery = function(element, layout) {
        layout = layout !== undefined ? layout : 'standard';

        const options = {
            dots: false,
            margin: 10,
            rtl: isRTL()
        };
        const layoutOptions = {
            standard: {
                responsive: {
                    1200: {items: 5},
                    992: {items: 4},
                    768: {items: 3},
                    480: {items: 5},
                    380: {items: 4},
                    0: {items: 3}
                }
            },
            sidebar: {
                responsive: {
                    768: {items: 4},
                    480: {items: 5},
                    380: {items: 4},
                    0: {items: 3}
                }
            },
            columnar: {
                responsive: {
                    768: {items: 4},
                    480: {items: 5},
                    380: {items: 4},
                    0: {items: 3}
                }
            },
            quickview: {
                responsive: {
                    1200: {items: 5},
                    768: {items: 4},
                    480: {items: 5},
                    380: {items: 4},
                    0: {items: 3}
                }
            }
        };

        const gallery = $(element);

        const image = gallery.find('.product-gallery-featured .owl-carousel');
        const carousel = gallery.find('.product-gallery-carousel .owl-carousel');

        image
            .owlCarousel({items: 1, dots: false, rtl: isRTL()})
            .on('changed.owl.carousel', syncPosition);

        carousel
            .on('initialized.owl.carousel', function () {
                carousel.find('.product-gallery-carousel-item').eq(0).addClass('product-gallery-carousel-item--active');
            })
            .owlCarousel($.extend({}, options, layoutOptions[layout]));

        carousel.on('click', '.owl-item', function(e){
            e.preventDefault();

            image.data('owl.carousel').to($(this).index(), 300, true);
        });

        gallery.find('.product-gallery-zoom').on('click', function() {
            openPhotoSwipe(image.find('.owl-item.active').index());
        });

        image.on('click', '.owl-item a', function(event) {
            event.preventDefault();

            openPhotoSwipe($(this).closest('.owl-item').index());
        });

        function getIndexDependOnDir(index) {
            // we need to invert index id direction === 'rtl' because photoswipe do not support rtl
            if (isRTL()) {
                return image.find('.owl-item img').length - 1 - index;
            }

            return index;
        }

        function openPhotoSwipe(index) {
            const photoSwipeImages = image.find('.owl-item a').toArray().map(function(element) {
                const img = $(element).find('img')[0];
                const width = $(element).data('width') || img.naturalWidth;
                const height = $(element).data('height') || img.naturalHeight;

                return {
                    src: element.href,
                    msrc: element.href,
                    w: width,
                    h: height,
                };
            });

            if (isRTL()) {
                photoSwipeImages.reverse();
            }

            const photoSwipeOptions = {
                getThumbBoundsFn: function(index) {
                    const imageElements = image.find('.owl-item img').toArray();
                    const dirDependentIndex = getIndexDependOnDir(index);

                    if (!imageElements[dirDependentIndex]) {
                        return null;
                    }

                    const imageElement = imageElements[dirDependentIndex];
                    const pageYScroll = window.pageYOffset || document.documentElement.scrollTop;
                    const rect = imageElement.getBoundingClientRect();

                    return {x: rect.left, y: rect.top + pageYScroll, w: rect.width};
                },
                index: getIndexDependOnDir(index),
                bgOpacity: .9,
                history: false
            };

            const photoSwipeGallery = new PhotoSwipe($('.pswp')[0], PhotoSwipeUI_Default, photoSwipeImages, photoSwipeOptions);

            photoSwipeGallery.listen('beforeChange', function() {
                image.data('owl.carousel').to(getIndexDependOnDir(photoSwipeGallery.getCurrentIndex()), 0, true);
            });

            photoSwipeGallery.init();
        }

        function syncPosition (el) {
            let current = el.item.index;

            carousel
                .find('.product-gallery-carousel-item')
                .removeClass('product-gallery-carousel-item--active')
                .eq(current)
                .addClass('product-gallery-carousel-item--active');
            const onscreen = carousel.find('.owl-item.active').length - 1;
            const start = carousel.find('.owl-item.active').first().index();
            const end = carousel.find('.owl-item.active').last().index();

            if (current > end) {
                carousel.data('owl.carousel').to(current, 100, true);
            }
            if (current < start) {
                carousel.data('owl.carousel').to(current - onscreen, 100, true);
            }
        }
    };

    $(function() {
        $('.product').each(function () {
            const gallery = $(this).find('.product-gallery');

            if (gallery.length > 0) {
                initProductGallery(gallery[0], $(this).data('layout'));
            }
        });
    });


    /*
    // Checkout payment methods
    */
    $(function () {
        $('[name="checkout_payment_method"]').on('change', function () {
            const currentItem = $(this).closest('.payment-methods-item');

            $(this).closest('.payment-methods-list').find('.payment-methods-item').each(function (i, element) {
                const links = $(element);
                const linksContent = links.find('.payment-methods-item-container');

                if (element !== currentItem[0]) {
                    const startHeight = linksContent.height();

                    linksContent.css('height', startHeight + 'px');
                    links.removeClass('payment-methods-item--active');
                    linksContent.height(); // force reflow

                    linksContent.css('height', '');
                } else {
                    const startHeight = linksContent.height();

                    links.addClass('payment-methods-item--active');

                    const endHeight = linksContent.height();

                    linksContent.css('height', startHeight + 'px');
                    linksContent.height(); // force reflow
                    linksContent.css('height', endHeight + 'px');
                }
            });
        });

        $('.payment-methods-item-container').on('transitionend', function (event) {
            if (event.originalEvent.propertyName === 'height') {
                $(this).css('height', '');
            }
        });
    });


    /*
    // collapse
    */
    $(function () {
        $('[data-collapse]').each(function (i, element) {
            const collapse = element;

            $('[data-collapse-trigger]', collapse).on('click', function () {
                const openedClass = $(this).closest('[data-collapse-opened-class]').data('collapse-opened-class');
                const item = $(this).closest('[data-collapse-item]');
                const content = item.children('[data-collapse-content]');
                const itemParents = item.parents();

                itemParents.slice(0, itemParents.index(collapse) + 1).filter('[data-collapse-item]').css('height', '');

                if (item.is('.' + openedClass)) {
                    const startHeight = content.height();

                    content.css('height', startHeight + 'px');
                    item.removeClass(openedClass);

                    content.height(); // force reflow
                    content.css('height', '');
                } else {
                    const startHeight = content.height();

                    item.addClass(openedClass);

                    const endHeight = content.height();

                    content.css('height', startHeight + 'px');
                    content.height(); // force reflow
                    content.css('height', endHeight + 'px');
                }
            });

            $('[data-collapse-content]', collapse).on('transitionend', function (event) {
                if (event.originalEvent.propertyName === 'height') {
                    $(this).css('height', '');
                }
            });
        });
    });


    /*
    // price filter
    */
    $(function () {
        $('.filter-price').each(function (i, element) {
            const min = $(element).data('min');
            const max = $(element).data('max');
            const from = $(element).data('from');
            const to = $(element).data('to');
            const slider = element.querySelector('.filter-price-slider');

            noUiSlider.create(slider, {
                start: [from, to],
                connect: true,
                direction: isRTL() ? 'rtl' : 'ltr',
                range: {
                    'min': min,
                    'max': max
                }
            });

            const titleValues = [
                $(element).find('.filter-price-min-value')[0],
                $(element).find('.filter-price-max-value')[0]
            ];

            slider.noUiSlider.on('update', function (values, handle) {
                titleValues[handle].innerHTML = values[handle];
            });
        });
    });


    /*
    // mobilemenu
    */
    $(function () {
        const body = $('body');
        const mobilemenu = $('.mobilemenu');

        if (mobilemenu.length) {
            const open = function() {
                const bodyWidth = body.width();
                body.css('overflow', 'hidden');
                body.css('paddingRight', (body.width() - bodyWidth) + 'px');

                mobilemenu.addClass('mobilemenu--open');
            };
            const close = function() {
                body.css('overflow', '');
                body.css('paddingRight', '');

                mobilemenu.removeClass('mobilemenu--open');
            };


            $('.mobile-header-menu-button').on('click', function() {
                open();
            });
            $('.mobilemenu-backdrop, .mobilemenu-close').on('click', function() {
                close();
            });
        }
    });


    /*
    // tooltips
    */
    $(function () {
        $('[data-toggle="tooltip"]').tooltip({trigger: 'hover'});
    });


    /*
    // layout switcher
    */
    $(function () {
        $('.layout-switcher-button').on('click', function() {
            const layoutSwitcher = $(this).closest('.layout-switcher');
            const productsView = $(this).closest('.products-view');
            const productsList = productsView.find('.products-list');

            layoutSwitcher.find('.layout-switcher-button').removeClass('layout-switcher-button--active');
            $(this).addClass('layout-switcher-button--active');

            productsList.attr('data-layout', $(this).attr('data-layout'));
            productsList.attr('data-with-features', $(this).attr('data-with-features'));
        });
    });


    /*
    // offcanvas filters
    */
    $(function () {
        const body = $('body');
        const blockSidebar = $('.block-sidebar');
        const mobileMedia = matchMedia('(max-width: 991px)');

        if (blockSidebar.length) {
            const open = function() {
                if (blockSidebar.is('.block-sidebar--offcanvas--mobile') && !mobileMedia.matches) {
                    return;
                }

                const bodyWidth = body.width();
                body.css('overflow', 'hidden');
                body.css('paddingRight', (body.width() - bodyWidth) + 'px');

                blockSidebar.addClass('block-sidebar--open');
            };
            const close = function() {
                body.css('overflow', '');
                body.css('paddingRight', '');

                blockSidebar.removeClass('block-sidebar--open');
            };
            const onChangeMedia = function() {
                if (blockSidebar.is('.block-sidebar--open.block-sidebar--offcanvas--mobile') && !mobileMedia.matches) {
                    close();
                }
            };

            $('.filters-button').on('click', function() {
                open();
            });
            $('.block-sidebar-backdrop, .block-sidebar-close').on('click', function() {
                close();
            });

            if (mobileMedia.addEventListener) {
                mobileMedia.addEventListener('change', onChangeMedia);
            } else {
                mobileMedia.addListener(onChangeMedia);
            }
        }
    });

    /*
    // .block-finder
    */
    $(function () {
        $('.block-finder-select').on('change', function() {
            const item = $(this).closest('.block-finder-form-item');

            if ($(this).val() !== 'none') {
                item.find('~ .block-finder-form-item:eq(0) .block-finder-select').prop('disabled', false).val('none');
                item.find('~ .block-finder-form-item:gt(0) .block-finder-select').prop('disabled', true).val('none');
            } else {
                item.find('~ .block-finder-form-item .block-finder-select').prop('disabled', true).val('none');
            }

            item.find('~ .block-finder-form-item .block-finder-select').trigger('change.select2');
        });
    });

    /*
    // select2
    */
    $(function () {
        $('.form-control-select2, .block-finder-select').select2({width: ''});
    });
})(jQuery);