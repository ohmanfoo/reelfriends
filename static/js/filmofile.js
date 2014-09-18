var start = function () {
    'use strict';
    var config = {
        filmsContainer : 'box box2',
        myfilmsContainer : 'box box3',
        films : 'films',
        myfilms : 'myfilms',
        orientation : (window.innerHeight + 40 >= window.innerWidth),
        sm : '39.22222%',
        med : '45.25555%',
        large : '100%'
    },
        filmsContent = document.getElementById(config.films),
        myfilmsContent = document.getElementById(config.myfilms),
        getHeading = function (cat) {
            var categ = document.getElementsByClassName(cat);
            return categ;
        },
        filmsHead = getHeading(config.filmsContainer),
        myfilmsHead = getHeading(config.myfilmsContainer),
        onLoadCheck = function () {
            if (config.orientation) {
                filmsContent.style.width = config.large;
                myfilmsContent.style.width = config.large;
            } else {
                myfilmsContent.style.width = config.sm;
                filmsContent.style.width = config.med;
            }
            myfilmsContent.style.height = '100%';
            filmsContent.style.height = '100%';
        },
        onClick = function (content, other) {
            if (content.style.display === 'none') {
                content.style.display = 'block';
                if (other.style.display === 'block') {
                    content.style.width = config.med;
                    other.style.width = config.med;
                } else {
                    other.style.display = 'none';
                    content.style.width = config.large;
                }
            } else {
                if (content.style.display === 'block') {
                    content.style.display = 'none';
                    other.style.width = config.large;
                } else {
                    content.style.display = 'none';
                    other.style.width = config.large;
                }
            }
        };
    filmsHead[0].onclick = function () {
        return onClick(filmsContent, myfilmsContent);
    };
    myfilmsHead[0].onclick = function () {
        return onClick(myfilmsContent, filmsContent);
    };
    onLoadCheck();
};
document.onreadystatechange = function () {
    'use strict';
    if (document.readyState === 'complete') {
        start();
    }
};
