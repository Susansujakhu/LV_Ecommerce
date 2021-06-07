(function($) {
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

    $(function () {
        /*
        // Touch Click
        */
        function touchClick(elements, callback) {
            elements = $(elements);

            let touchStartData = null;

            const onTouchstart = function(event){
                const originalEvent = event.originalEvent;

                if (originalEvent.touches.length !== 1) {
                    touchStartData = null;
                    return;
                }

                touchStartData = {
                    target: originalEvent.currentTarget,
                    touch: originalEvent.changedTouches[0],
                    timestamp: (new Date).getTime(),
                };
            };
            const onTouchEnd = function(event){
                const originalEvent = event.originalEvent;

                if (
                    !touchStartData ||
                    originalEvent.changedTouches.length !== 1 ||
                    originalEvent.changedTouches[0].identity !== touchStartData.touch.identity
                ) {
                    return;
                }

                const timestamp = (new Date).getTime();
                const touch = originalEvent.changedTouches[0];
                const distance = Math.abs(
                    Math.sqrt(
                        Math.pow(touchStartData.touch.screenX - touch.screenX, 2) +
                        Math.pow(touchStartData.touch.screenY - touch.screenY, 2)
                    )
                );

                if (touchStartData.target === originalEvent.currentTarget && timestamp - touchStartData.timestamp < 500 && distance < 10) {
                    callback(event);
                }
            };

            elements.on('touchstart', onTouchstart);
            elements.on('touchend', onTouchEnd);

            return function() {
                elements.off('touchstart', onTouchstart);
                elements.off('touchend', onTouchEnd);
            };
        }

        // call this in touchstart/touchend event handler
        function preventTouchClick() {
            const onClick = function(event){
                event.preventDefault();

                document.removeEventListener('click', onClick);
            };
            document.addEventListener('click', onClick);
            setTimeout(function() {
                document.removeEventListener('click', onClick);
            }, 100);
        }


        /*
        // topbar dropdown
        */
        $('.topbar-dropdown-btn').on('click', function() {
            $(this).closest('.topbar-dropdown').toggleClass('topbar-dropdown--opened');
        });

        document.addEventListener('click', function(event) {
            $('.topbar-dropdown')
                .not($(event.target).closest('.topbar-dropdown'))
                .removeClass('topbar-dropdown--opened');
        }, true);

        touchClick(document, function(event) {
            $('.topbar-dropdown')
                .not($(event.target).closest('.topbar-dropdown'))
                .removeClass('topbar-dropdown--opened');
        });


        /*
        // search suggestions
        */
        $('.search').each(function(index, element) {
            let xhr;
            const search = $(element);
            const categories = search.find('.search-categories');
            const input = search.find('.search-input');
            const suggestions = search.find('.search-suggestions');
            const outsideClick = function(event) {
                // If the inner element still has focus, ignore the click.
                if ($(document.activeElement).closest('.search').is(search)) {
                    return;
                }

                search
                    .not($(event.target).closest('.search'))
                    .removeClass('search--suggestions-open');
            };
            const setSuggestion = function(html) {
                if (html) {
                    suggestions.html(html);
                }
                search.toggleClass('search--has-suggestions', !!html);
            };

            search.on('focusout', function() {
                setTimeout(function(){
                    if (document.activeElement === document.body) {
                        return;
                    }

                    // Close suggestions if the focus received an external element.
                    search
                        .not($(document.activeElement).closest('.search'))
                        .removeClass('search--suggestions-open');
                }, 10);
            });
            input.on('input', function() {
                if (xhr) {
                    // Abort previous AJAX request.
                    xhr.abort();
                }

                if (input.val()) {
                    // YOUR AJAX REQUEST HERE.
                    xhr = $.ajax({
                        url: '/searchSuggestion',
                        success: function(data) {
                            xhr = null;
                            setSuggestion(data);
                        }
                    });
                } else {
                    // Remove suggestions.
                    setSuggestion('');
                }
            });
            input.on('focus', function() {
                search.addClass('search--suggestions-open');
            });
            categories.on('focus', function() {
                search.removeClass('search--suggestions-open');
            });

            document.addEventListener('click', outsideClick, true);
            touchClick(document, outsideClick);

            if (input.is(document.activeElement)) {
                input.trigger('focus').trigger('input');
            }
        });


        /*
        // mobile search
        */
        const mobileSearch = $('.mobile-header-search');

        if (mobileSearch.length) {
            $('.indicator--mobile-search .indicator-button').on('click', function() {
                if (mobileSearch.is('.mobile-header-search--open')) {
                    mobileSearch.removeClass('mobile-header-search--open');
                } else {
                    mobileSearch.addClass('mobile-header-search--open');
                    mobileSearch.find('input')[0].focus();
                }
            });

            mobileSearch.find('.search-button--type--close').on('click', function() {
                mobileSearch.removeClass('mobile-header-search--open');
            });

            document.addEventListener('click', function(event) {
                if (!$(event.target).closest('.indicator--mobile-search, .mobile-header-search').length) {
                    mobileSearch.removeClass('mobile-header-search--open');
                }
            }, true);
        }


        /*
        // nav-links
        */
        function CNavLinks(element) {
            this.element = $(element);
            this.items = this.element.find('.nav-links-item');
            this.currentItem = null;

            this.element.data('navLinksInstance', this);

            this.onMouseenter = this.onMouseenter.bind(this);
            this.onMouseleave = this.onMouseleave.bind(this);
            this.onGlobalTouchClick = this.onGlobalTouchClick.bind(this);
            this.onTouchClick = this.onTouchClick.bind(this);

            // add event listeners
            this.items.on('mouseenter', this.onMouseenter);
            this.items.on('mouseleave', this.onMouseleave);
            touchClick(document, this.onGlobalTouchClick);
            touchClick(this.items, this.onTouchClick);
        }
        CNavLinks.prototype.onGlobalTouchClick = function(event) {
            // check that the click was outside the element
            if (this.element.not($(event.target).closest('.nav-links')).length) {
                this.unsetCurrentItem();
            }
        };
        CNavLinks.prototype.onTouchClick = function(event) {
            if (event.cancelable) {
                const targetItem = $(event.currentTarget);

                if (this.currentItem && this.currentItem.is(targetItem)) {
                    return;
                }

                if (this.hasSubmenu(targetItem)) {
                    event.preventDefault();

                    if (this.currentItem) {
                        this.currentItem.trigger('mouseleave');
                    }

                    targetItem.trigger('mouseenter');
                }
            }
        };
        CNavLinks.prototype.onMouseenter = function(event) {
            this.setCurrentItem($(event.currentTarget));
        };
        CNavLinks.prototype.onMouseleave = function() {
            this.unsetCurrentItem();
        };
        CNavLinks.prototype.setCurrentItem = function(item) {
            this.currentItem = item;
            this.currentItem.addClass('nav-links-item--hover');

            this.openSubmenu(this.currentItem);
        };
        CNavLinks.prototype.unsetCurrentItem = function() {
            if (this.currentItem) {
                this.closeSubmenu(this.currentItem);

                this.currentItem.removeClass('nav-links-item--hover');
                this.currentItem = null;
            }
        };
        CNavLinks.prototype.hasSubmenu = function(item) {
            return !!item.children('.nav-links-submenu').length;
        };
        CNavLinks.prototype.openSubmenu = function(item) {
            const submenu = item.children('.nav-links-submenu');

            if (!submenu.length) {
                return;
            }

            submenu.addClass('nav-links-submenu--display');

            // calculate max height
            const submenuTop = submenu.offset().top - $(window).scrollTop();
            const viewportHeight = window.innerHeight;
            const paddingBottom = 20;

            submenu.css('maxHeight', (viewportHeight - submenuTop - paddingBottom) + 'px');
            submenu.addClass('nav-links-submenu--open');

            // megamenu position
            if (submenu.hasClass('nav-links-submenu--type--megamenu')) {
                const container = submenu.offsetParent();
                const containerWidth = container.width();
                const megamenuWidth = submenu.width();

                if (isRTL()) {
                    const itemPosition = containerWidth - (item.position().left + item.width());
                    const megamenuPosition = Math.round(Math.min(itemPosition, containerWidth - megamenuWidth));

                    submenu.css('right', megamenuPosition + 'px');
                } else {
                    const itemPosition = item.position().left;
                    const megamenuPosition = Math.round(Math.min(itemPosition, containerWidth - megamenuWidth));

                    submenu.css('left', megamenuPosition + 'px');
                }
            }
        };
        CNavLinks.prototype.closeSubmenu = function(item) {
            const submenu = item.children('.nav-links-submenu');

            if (!submenu.length) {
                return;
            }

            submenu.removeClass('nav-links-submenu--display');
            submenu.removeClass('nav-links-submenu--open');
            submenu.css('maxHeight', '');

            if (submenu && submenu.is('.nav-links-submenu--type--menu')) {
                const submenuInstance = submenu.find('> .menu').data('menuInstance');

                if (submenuInstance) {
                    submenuInstance.unsetCurrentItem();
                }
            }
        };

        $('.nav-links').each(function() {
            new CNavLinks(this);
        });


        /*
        // menu
        */
        function CMenu(element) {
            this.element = $(element);
            this.container = this.element.find('> .menu-submenus-container');
            this.items = this.element.find('> .menu-list > .menu-item');
            this.currentItem = null;

            this.element.data('menuInstance', this);

            this.onMouseenter = this.onMouseenter.bind(this);
            this.onMouseleave = this.onMouseleave.bind(this);
            this.onTouchClick = this.onTouchClick.bind(this);

            // add event listeners
            this.items.on('mouseenter', this.onMouseenter);
            this.element.on('mouseleave', this.onMouseleave);
            touchClick(this.items, this.onTouchClick);
        }
        CMenu.prototype.onMouseenter = function(event) {
            const targetItem = $(event.currentTarget);

            if (this.currentItem && targetItem.is(this.currentItem)) {
                return;
            }

            this.unsetCurrentItem();
            this.setCurrentItem(targetItem);
        };
        CMenu.prototype.onMouseleave = function() {
            this.unsetCurrentItem();
        };
        CMenu.prototype.onTouchClick = function(event) {
            const targetItem = $(event.currentTarget);

            if (this.currentItem && this.currentItem.is(targetItem)) {
                return;
            }

            if (this.hasSubmenu(targetItem)) {
                preventTouchClick();

                this.unsetCurrentItem();
                this.setCurrentItem(targetItem);
            }
        };
        CMenu.prototype.setCurrentItem = function(item) {
            this.currentItem = item;
            this.currentItem.addClass('menu-item--hover');

            this.openSubmenu(this.currentItem);
        };
        CMenu.prototype.unsetCurrentItem = function() {
            if (this.currentItem) {
                this.closeSubmenu(this.currentItem);

                this.currentItem.removeClass('menu-item--hover');
                this.currentItem = null;
            }
        };
        CMenu.prototype.getSubmenu = function(item) {
            let submenu = item.find('> .menu-submenu');

            if (submenu.length) {
                this.container.append(submenu);
                item.data('submenu', submenu);
            }

            return item.data('submenu');
        };
        CMenu.prototype.hasSubmenu = function(item) {
            return !!this.getSubmenu(item);
        };
        CMenu.prototype.openSubmenu = function(item) {
            const submenu = this.getSubmenu(item);

            if (!submenu) {
                return;
            }

            submenu.addClass('menu-submenu--display');

            // calc submenu position
            const menuTop = this.element.offset().top - $(window).scrollTop();
            const itemTop = item.find('> .menu-item-submenu-offset').offset().top - $(window).scrollTop();
            const viewportHeight = window.innerHeight;
            const paddingY = 20;
            const maxHeight = viewportHeight - paddingY * 2;

            submenu.css('maxHeight', maxHeight + 'px');

            const submenuHeight = submenu.height();
            const position = Math.min(
                Math.max(
                    itemTop - menuTop,
                    0
                ),
                (viewportHeight - paddingY - submenuHeight) - menuTop
            );

            submenu.css('top', position + 'px');
            submenu.addClass('menu-submenu--open');

            if (isRTL()) {
                const submenuLeft = this.element.offset().left - submenu.width();

                if (submenuLeft < 0) {
                    submenu.addClass('menu-submenu--reverse');
                }
            } else {
                const submenuRight = this.element.offset().left + this.element.width() + submenu.width();

                if (submenuRight > $('body').innerWidth()) {
                    submenu.addClass('menu-submenu--reverse');
                }
            }
        };
        CMenu.prototype.closeSubmenu = function(item) {
            const submenu = this.getSubmenu(item);

            if (submenu) {
                submenu.removeClass('menu-submenu--display');
                submenu.removeClass('menu-submenu--open');
                submenu.removeClass('menu-submenu--reverse');

                const submenuInstance = submenu.find('> .menu').data('menuInstance');

                if (submenuInstance) {
                    submenuInstance.unsetCurrentItem();
                }
            }
        };
        $('.menu').each(function(){
            new CMenu($(this));
        });


        /*
        // indicator (dropcart, drop search)
        */
        function CIndicator(element) {
            this.element = $(element);
            this.dropdown = this.element.find('.indicator-dropdown');
            this.button = this.element.find('.indicator-button');
            this.trigger = null;

            this.element.data('indicatorInstance', this);

            if (this.element.hasClass('indicator--trigger--hover')) {
                this.trigger = 'hover';
            } else if (this.element.hasClass('indicator--trigger--click')) {
                this.trigger = 'click';
            }

            this.onMouseenter = this.onMouseenter.bind(this);
            this.onMouseleave = this.onMouseleave.bind(this);
            this.onTransitionend = this.onTransitionend.bind(this);
            this.onClick = this.onClick.bind(this);
            this.onGlobalClick = this.onGlobalClick.bind(this);

            // add event listeners
            this.element.on('mouseenter', this.onMouseenter);
            this.element.on('mouseleave', this.onMouseleave);
            this.dropdown.on('transitionend', this.onTransitionend);
            this.button.on('click', this.onClick);
            $(document).on('click', this.onGlobalClick);
            touchClick(document, this.onGlobalClick);

            this.element.find('.search-input').on('keydown', function(event) {
                const ESC_KEY_CODE = 27;

                if (event.which === ESC_KEY_CODE) {
                    const instance = $(this).closest('.indicator').data('indicatorInstance');

                    if (instance) {
                        instance.close();
                    }
                }
            });
        }
        CIndicator.prototype.toggle = function(){
            if (this.isOpen()) {
                this.close();
            } else {
                this.open();
            }
        };
        CIndicator.prototype.onMouseenter = function(){
            this.element.addClass('indicator--hover');

            if (this.trigger === 'hover') {
                this.open();
            }
        };
        CIndicator.prototype.onMouseleave = function(){
            this.element.removeClass('indicator--hover');

            if (this.trigger === 'hover') {
                this.close();
            }
        };
        CIndicator.prototype.onTransitionend = function(event){
            if (
                this.dropdown.is(event.target) &&
                event.originalEvent.propertyName === 'visibility' &&
                !this.isOpen()
            ) {
                this.element.removeClass('indicator--display');
            }
        };
        CIndicator.prototype.onClick = function(event){
            if (this.trigger !== 'click') {
                return;
            }

            if (event.cancelable) {
                event.preventDefault();
            }

            this.toggle();
        };
        CIndicator.prototype.onGlobalClick = function(event){
            // check that the click was outside the element
            if (this.element.not($(event.target).closest('.indicator')).length) {
                this.close();
            }
        };
        CIndicator.prototype.isOpen = function(){
            return this.element.is('.indicator--open');
        };
        CIndicator.prototype.open = function(){
            this.element.addClass('indicator--display');
            this.element.width(); // force reflow
            this.element.addClass('indicator--open');
            this.element.find('.search-input').focus();

            const dropdownTop = this.dropdown.offset().top - $(window).scrollTop();
            const viewportHeight = window.innerHeight;
            const paddingBottom = 20;

            this.dropdown.css('maxHeight', (viewportHeight - dropdownTop - paddingBottom) + 'px');
        };
        CIndicator.prototype.close = function(){
            this.element.removeClass('indicator--open');
        };
        CIndicator.prototype.closeImmediately = function(){
            this.element.removeClass('indicator--open');
            this.element.removeClass('indicator--display');
        };

        $('.indicator').each(function() {
            new CIndicator(this);
        });


        /*
        // departments, sticky header
        */
        $(function() {
            /*
            // departments
            */
            const CDepartments = function(element) {
                const self = this;

                element.data('departmentsInstance', self);

                this.element = element;
                this.container = this.element.find('.departments-submenus-container');
                this.linksWrapper = this.element.find('.departments-links-wrapper');
                this.body = this.element.find('.departments-body');
                this.button = this.element.find('.departments-button');
                this.items = this.element.find('.departments-item');
                this.mode = this.element.is('.departments--fixed') ? 'fixed' : 'normal';
                this.fixedBy = $(this.element.data('departments-fixed-by'));
                this.fixedHeight = 0;
                this.currentItem = null;

                if (this.mode === 'fixed' && this.fixedBy.length) {
                    this.fixedHeight = this.fixedBy.offset().top - this.body.offset().top + this.fixedBy.outerHeight();
                    this.body.css('height', this.fixedHeight + 'px');
                }

                this.linksWrapper.on('transitionend', function (event) {
                    if (event.originalEvent.propertyName === 'height') {
                        $(this).css('height', '');
                        $(this).closest('.departments').removeClass('departments--transition');
                    }
                });

                this.onButtonClick = this.onButtonClick.bind(this);
                this.onGlobalClick = this.onGlobalClick.bind(this);
                this.onMouseenter = this.onMouseenter.bind(this);
                this.onMouseleave = this.onMouseleave.bind(this);
                this.onTouchClick = this.onTouchClick.bind(this);

                // add event listeners
                this.button.on('click', this.onButtonClick);
                document.addEventListener('click', this.onGlobalClick, true);
                touchClick(document, this.onGlobalClick);
                this.items.on('mouseenter', this.onMouseenter);
                this.linksWrapper.on('mouseleave', this.onMouseleave);
                touchClick(this.items, this.onTouchClick);

            };
            CDepartments.prototype.onButtonClick = function(event) {
                event.preventDefault();

                if (this.element.is('.departments--open')) {
                    this.close();
                } else {
                    this.open();
                }
            };
            CDepartments.prototype.onGlobalClick = function(event) {
                if (this.element.not($(event.target).closest('.departments')).length) {
                    if (this.element.is('.departments--open')) {
                        this.close();
                    }
                }
            };
            CDepartments.prototype.setMode = function(mode) {
                this.mode = mode;

                if (this.mode === 'normal') {
                    this.element.removeClass('departments--fixed');
                    this.element.removeClass('departments--open');
                    this.body.css('height', 'auto');
                }
                if (this.mode === 'fixed') {
                    this.element.addClass('departments--fixed');
                    this.element.addClass('departments--open');
                    this.body.css('height', this.fixedHeight + 'px');
                    $('.departments-links-wrapper', this.element).css('maxHeight', '');
                }
            };
            CDepartments.prototype.close = function() {
                if (this.element.is('.departments--fixed')) {
                    return;
                }

                const content = this.element.find('.departments-links-wrapper');
                const startHeight = content.height();

                content.css('height', startHeight + 'px');
                this.element
                    .addClass('departments--transition')
                    .removeClass('departments--open');

                content.height(); // force reflow
                content.css('height', '');
                content.css('maxHeight', '');

                this.unsetCurrentItem();
            };
            CDepartments.prototype.closeImmediately = function() {
                if (this.element.is('.departments--fixed')) {
                    return;
                }

                const content = this.element.find('.departments-links-wrapper');

                this.element.removeClass('departments--open');

                content.css('height', '');
                content.css('maxHeight', '');

                this.unsetCurrentItem();
            };
            CDepartments.prototype.open = function() {
                const content = this.element.find('.departments-links-wrapper');
                const startHeight = content.height();

                this.element
                    .addClass('departments--transition')
                    .addClass('departments--open');

                const documentHeight = document.documentElement.clientHeight;
                const paddingBottom = 20;
                const contentRect = content[0].getBoundingClientRect();
                const endHeight = Math.min(content.height(), documentHeight - paddingBottom - contentRect.top);

                content.css('height', startHeight + 'px');
                content.height(); // force reflow
                content.css('maxHeight', endHeight + 'px');
                content.css('height', endHeight + 'px');
            };
            CDepartments.prototype.onMouseenter = function(event) {
                const targetItem = $(event.currentTarget);

                if (this.currentItem && targetItem.is(this.currentItem)) {
                    return;
                }

                this.unsetCurrentItem();
                this.setCurrentItem(targetItem);
            };
            CDepartments.prototype.onMouseleave = function() {
                this.unsetCurrentItem();
            };
            CDepartments.prototype.onTouchClick = function(event) {
                const targetItem = $(event.currentTarget);

                if (this.currentItem && this.currentItem.is(targetItem)) {
                    return;
                }

                if (this.hasSubmenu(targetItem)) {
                    preventTouchClick();

                    this.unsetCurrentItem();
                    this.setCurrentItem(targetItem);
                }
            };
            CDepartments.prototype.setCurrentItem = function(item) {
                this.unsetCurrentItem();

                this.currentItem = item;
                this.currentItem.addClass('departments-item--hover');

                this.openSubmenu(this.currentItem);
            };
            CDepartments.prototype.unsetCurrentItem = function() {
                if (this.currentItem) {
                    this.closeSubmenu(this.currentItem);

                    this.currentItem.removeClass('departments-item--hover');
                    this.currentItem = null;
                }
            };
            CDepartments.prototype.getSubmenu = function(item) {
                let submenu = item.find('> .departments-submenu');

                if (submenu.length) {
                    this.container.append(submenu);

                    item.data('submenu', submenu);
                }

                return item.data('submenu');
            };
            CDepartments.prototype.hasSubmenu = function(item) {
                return !!this.getSubmenu(item);
            };
            CDepartments.prototype.openSubmenu = function(item) {
                const submenu = this.getSubmenu(item);

                if (submenu) {
                    submenu.addClass('departments-submenu--open');

                    const documentHeight = document.documentElement.clientHeight;
                    const paddingBottom = 20;

                    if (submenu.hasClass('departments-submenu--type--megamenu')) {
                        const submenuTop = submenu.offset().top - $(window).scrollTop();
                        submenu.css('maxHeight', (documentHeight - submenuTop - paddingBottom) + 'px');
                    }

                    if (submenu.hasClass('departments-submenu--type--menu')) {
                        submenu.css('maxHeight', (documentHeight - paddingBottom - Math.min(
                            paddingBottom,
                            this.body.offset().top - $(window).scrollTop()
                        )) + 'px');

                        const submenuHeight = submenu.height();
                        const itemTop = this.currentItem.offset().top - $(window).scrollTop();
                        const containerTop = this.container.offset().top - $(window).scrollTop();

                        submenu.css('top', (Math.min(itemTop, documentHeight - paddingBottom - submenuHeight) - containerTop) + 'px');
                    }
                }
            };
            CDepartments.prototype.closeSubmenu = function(item) {
                const submenu = item.data('submenu');

                if (submenu) {
                    submenu.removeClass('departments-submenu--open');

                    if (submenu.is('.departments-submenu--type--menu')) {
                        submenu.find('> .menu').data('menuInstance').unsetCurrentItem();
                    }
                }
            };

            const departmentsElement = $('.departments');
            const departments = departmentsElement.length ? new CDepartments(departmentsElement) : null;


            /*
            // sticky nav-panel
            */
            const nav = $('.nav-panel--sticky');

            if (nav.length) {
                const mode = nav.data('sticky-mode') ? nav.data('sticky-mode') : 'alwaysOnTop'; // one of [alwaysOnTop, pullToShow]
                const media = matchMedia('(min-width: 992px)');
                const departmentsMode = departments ? departments.mode : null;

                let stuck = false;
                let shown = false;
                let scrollDistance = 0;
                let scrollPosition = 0;
                let positionWhenToFix = function() { return 0; };
                let positionWhenToStick = function() { return 0; };

                const closeAllSubmenus = function() {
                    if (departments) {
                        departments.closeImmediately();
                    }
                    $('.nav-links').data('navLinksInstance').unsetCurrentItem();
                    $('.indicator').each(function() {
                        $(this).data('indicatorInstance').closeImmediately();
                    });
                };

                const show = function() {
                    nav.addClass('nav-panel--show');
                    shown = true;
                    $(document).trigger('stroyka.header.sticky.show');
                };
                const hide = function() {
                    nav.removeClass('nav-panel--show');
                    shown = false;
                    $(document).trigger('stroyka.header.sticky.hide');
                };

                const onScroll = function() {
                    const scrollDelta = window.pageYOffset - scrollPosition;

                    if ((scrollDelta < 0) !== (scrollDistance < 0)) {
                        scrollDistance = 0;
                    }

                    scrollPosition = window.pageYOffset;
                    scrollDistance += scrollDelta;

                    if (window.pageYOffset > positionWhenToStick()) {
                        if (!stuck) {
                            nav.addClass('nav-panel--stuck');
                            nav.css('transitionDuration', '0s');

                            if (mode === 'alwaysOnTop') {
                                show();
                            }

                            nav.height(); // force reflow
                            nav.css('transitionDuration', '');
                            stuck = true;

                            if (departments && departmentsMode === 'fixed') {
                                departments.setMode('normal');
                            }

                            closeAllSubmenus();
                        }

                        if (mode === 'pullToShow') {
                            const distanceToShow = 10; // in pixels
                            const distanceToHide = 25; // in pixels

                            if (scrollDistance < -distanceToShow && !nav.hasClass('nav-panel--show')) {
                                show();
                            }
                            if (scrollDistance > distanceToHide && nav.hasClass('nav-panel--show')) {
                                hide();
                                closeAllSubmenus();
                            }
                        }
                    } else if (window.pageYOffset <= positionWhenToFix()) {
                        if (stuck) {
                            nav.removeClass('nav-panel--stuck');
                            stuck = false;
                            hide();

                            if (departments && departmentsMode === 'fixed') {
                                departments.setMode('fixed');
                            }

                            closeAllSubmenus();
                        }
                    }
                };

                const onMediaChange = function() {
                    if (media.matches) {
                        scrollDistance = 0;
                        scrollPosition = window.pageYOffset;

                        const navPanelTop = nav.offset().top;
                        const navPanelBottom = navPanelTop + nav.outerHeight();
                        const departmentsBottom = departments ? departments.body.offset().top + departments.body.outerHeight() : 0;

                        if (departments && departmentsMode === 'fixed' && departmentsBottom > navPanelBottom) {
                            positionWhenToFix = positionWhenToStick = function () {
                                return departmentsBottom;
                            };
                        } else {
                            if (mode === 'alwaysOnTop') {
                                positionWhenToFix = positionWhenToStick = function() {
                                    return navPanelTop;
                                };
                            } else {
                                positionWhenToFix = function () {
                                    return shown ? navPanelTop : navPanelBottom;
                                };
                                positionWhenToStick = function () {
                                    return navPanelBottom;
                                };
                            }
                        }

                        window.addEventListener('scroll', onScroll, passiveSupported ? {passive: true} : false);

                        onScroll();
                    } else {
                        if (stuck) {
                            nav.removeClass('nav-panel--stuck');
                            stuck = false;
                            hide();

                            if (departments && departmentsMode === 'fixed') {
                                departments.setMode('fixed');
                            }

                            closeAllSubmenus();
                        }

                        window.removeEventListener('scroll', onScroll, passiveSupported ? {passive: true} : false);
                    }
                };

                if (media.addEventListener) {
                    media.addEventListener('change', onMediaChange);
                } else {
                    media.addListener(onMediaChange);
                }

                onMediaChange();
            }


            /*
            // sticky mobile-header
            */
            const mobileHeader = $('.mobile-header--sticky');
            const mobileHeaderPanel = mobileHeader.find('.mobile-header-panel');

            if (mobileHeader.length) {
                const mode = mobileHeader.data('sticky-mode') ? mobileHeader.data('sticky-mode') : 'alwaysOnTop'; // one of [alwaysOnTop, pullToShow]
                const media = matchMedia('(min-width: 992px)');

                let stuck = false;
                let shown = false;
                let scrollDistance = 0;
                let scrollPosition = 0;
                let positionWhenToFix = 0;
                let positionWhenToStick = 0;

                const show = function() {
                    mobileHeader.addClass('mobile-header--show');
                    shown = true;
                    $(document).trigger('stroyka.header.sticky.show');
                };
                const hide = function() {
                    mobileHeader.removeClass('mobile-header--show');
                    shown = false;
                    $(document).trigger('stroyka.header.sticky.hide');
                };

                const onScroll = function() {
                    const scrollDelta = window.pageYOffset - scrollPosition;

                    if ((scrollDelta < 0) !== (scrollDistance < 0)) {
                        scrollDistance = 0;
                    }

                    scrollPosition = window.pageYOffset;
                    scrollDistance += scrollDelta;

                    if (window.pageYOffset > positionWhenToStick) {
                        if (!stuck) {
                            mobileHeader.addClass('mobile-header--stuck');
                            mobileHeaderPanel.css('transitionDuration', '0s');

                            if (mode === 'alwaysOnTop') {
                                show();
                            }

                            mobileHeader.height(); // force reflow
                            mobileHeaderPanel.css('transitionDuration', '');
                            stuck = true;
                        }

                        if (mode === 'pullToShow') {
                            if (window.pageYOffset > positionWhenToFix) {
                                const distanceToShow = 10; // in pixels
                                const distanceToHide = 25; // in pixels

                                if (scrollDistance < -distanceToShow && !shown) {
                                    show();
                                }
                                if (scrollDistance > distanceToHide && shown) {
                                    hide();
                                }
                            } else if (shown) {
                                hide();
                            }
                        }
                    } else if (window.pageYOffset <= positionWhenToFix) {
                        if (stuck) {
                            mobileHeader.removeClass('mobile-header--stuck');
                            stuck = false;
                            hide();
                        }
                    }
                };

                const onMediaChange = function() {
                    if (!media.matches) {
                        scrollDistance = 0;
                        scrollPosition = window.pageYOffset;
                        positionWhenToFix = mobileHeader.offset().top;
                        positionWhenToStick = positionWhenToFix + (mode === 'alwaysOnTop' ? 0 : mobileHeader.outerHeight());

                        window.addEventListener('scroll', onScroll, passiveSupported ? {passive: true} : false);

                        onScroll();
                    } else {
                        if (stuck) {
                            mobileHeader.removeClass('mobile-header--stuck');
                            mobileHeader.removeClass('mobile-header--show');
                            stuck = false;
                            shown = false;
                            $(document).trigger('stroyka.header.sticky.hide');
                        }

                        window.removeEventListener('scroll', onScroll, passiveSupported ? {passive: true} : false);
                    }
                };

                if (media.addEventListener) {
                    media.addEventListener('change', onMediaChange);
                } else {
                    media.addListener(onMediaChange);
                }

                onMediaChange();
            }
        });


        /*
        // offcanvas cart
        */
        (function() {
            const body = $('body');
            const cart = $('.dropcart--style--offcanvas');

            if (cart.length === 0) {
                return;
            }

            function cartIsHidden() {
                return window.getComputedStyle(cart[0]).visibility === 'hidden';
            }
            function showScrollbar() {
                body.css('overflow', '');
                body.css('paddingRight', '');
            }
            function hideScrollbar() {
                const bodyWidth = body.width();
                body.css('overflow', 'hidden');
                body.css('paddingRight', (body.width() - bodyWidth) + 'px');
            }
            function open() {
                hideScrollbar();

                cart.addClass('dropcart--open');
            }
            function close() {
                if (cartIsHidden()) {
                    showScrollbar();
                }

                cart.removeClass('dropcart--open');
            }

            $('[data-open="offcanvas-cart"]').on('click', function(event){
                if (!event.cancelable) {
                    return;
                }

                event.preventDefault();

                open();
            });

            cart.find('.dropcart-backdrop, .dropcart-close').on('click', function(){
                close();
            });

            cart.on('transitionend', function(event){
                if (cart.is(event.target) && event.originalEvent.propertyName === 'visibility' && cartIsHidden()) {
                    showScrollbar();
                }
            });
        })();

        /*
        // offcanvas account
        */
        (function() {
            const body = $('body');
            const account = $('.dropaccount--style--offcanvas');

            if (account.length === 0) {
                return;
            }

            function accountIsHidden() {
                return window.getComputedStyle(account[0]).visibility === 'hidden';
            }
            function showScrollbar() {
                body.css('overflow', '');
                body.css('paddingRight', '');
            }
            function hideScrollbar() {
                const bodyWidth = body.width();
                body.css('overflow', 'hidden');
                body.css('paddingRight', (body.width() - bodyWidth) + 'px');
            }
            function open() {
                hideScrollbar();

                account.addClass('dropaccount--open');
            }
            function close() {
                if (accountIsHidden()) {
                    showScrollbar();
                }

                account.removeClass('dropaccount--open');
            }

            $('[data-open="offcanvas-account"]').on('click', function(event){
                if (!event.cancelable) {
                    return;
                }

                event.preventDefault();

                open();
            });

            account.find('.dropaccount-backdrop, .dropaccount-close').on('click', function(){
                close();
            });

            account.on('transitionend', function(event){
                if (account.is(event.target) && event.originalEvent.propertyName === 'visibility' && accountIsHidden()) {
                    showScrollbar();
                }
            });
        })();
    });

})(jQuery);
