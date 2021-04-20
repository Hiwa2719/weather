
$(document).ready(function () {

    //add city
    let form = $('.add-city-form')

    form.hover(function () {
        form.css({
            opacity: 1,
            transition: 'opacity .3s'
        })
    }, function () {
        form.css({
            opacity: .3
        })
    })
    let mainSection = $('.main-section')

    form.on('submit', function (event) {
        event.preventDefault()

        let citiesDataRow = $('.cities-data .row').eq(0)
        citiesDataRow.append('<div class="col-10 col-sm-6 col-md-5 col-lg-4 col-xl-3 my-2">\n' +
            '                    <div class="city-card border rounded position-relative">\n' +
            '                        <div class="row close-row">\n' +
            '                            <div class="col">\n' +
            '                                <form method="POST">\n' +
            '                                    <!--                                            {% csrf_token %}-->\n' +
            '                                    <input type="hidden" name="city-name" value="{{ city.name }}">\n' +
            '                                    <input type="hidden" name="lat" value="{{ city.lat }}">\n' +
            '                                    <input type="hidden" name="lon" value="{{ city.lon }}">\n' +
            '                                    <button type="button" class="close" aria-label="Close">\n' +
            '                                        <i class="far fa-times-circle fa-sm"></i>\n' +
            '                                    </button>\n' +
            '                                </form>\n' +
            '                            </div>\n' +
            '                        </div>\n' +
            '                        <div class="card-detail">\n' +
            '                            <div class="row align-items-center">\n' +
            '                                <div class="col-md-4 col-lg-3 text-center">\n' +
            '                                    <img src="01d.png" class="" style="height: 100px" alt="...">\n' +
            '                                </div>\n' +
            '                                <div class="col-md-7">\n' +
            '                                    <div class="card-body pt-0 pt-md-4">\n' +
            '                                        <h3 class="card-title m-0">City Name</h3>\n' +
            '                                        <p class="card-text m-0"><small class="text-muted">City temp</small></p>\n' +
            '                                        <p class="card-text m-0">city.description}</p>\n' +
            '                                        <p class="card-text m-0 text-muted small">local time: city.local_time</p>\n' +
            '                                    </div>\n' +
            '                                </div>\n' +
            '                            </div>\n' +
            '                        </div>\n' +
            '                    </div>\n' +
            '                </div>')
        form[0].reset()
        mainSection.find('.main-body').removeClass('move-down').addClass('move-up')
        mainSection.find('.new-line-btn').removeClass('d-none')
        mainSection.find('.new-line-row').removeClass('d-none')
        // $.ajax({
        //     // url: "{% url 'weather:index' %}",
        //     method: 'POST',
        //     data: form.serialize(),
        //     success: function (data) {
        //         let citiesDataRow = $('.cities-data .row').eq(0)
        //         citiesDataRow.append(data.new_city)
        //         form[0].reset()
        //     },
        //     error: function (errorData) {
        //         let errorMessage = errorData.responseJSON.errorMessage
        //         let formErrors = $('.form-errors')
        //         if (formErrors){
        //             formErrors.remove()
        //         }
        //         let formRow = form.find('.row')
        //         formRow.append(
        //             '<div class="col-12 form-errors"><ul><p><li><strong class="text-danger">'+ errorMessage + '</strong></li></p></ul></div>'
        //         )
        //     }
        // })
    })

    //remove city from the list
    let citiesData = $('.cities-data')
    citiesData.on('click', '.close', function (event) {
        let $this = $(this)
        let form = $this.closest('form')
        let cityCard = $this.closest('.city-card').parent()
        cityCard.remove()
        let citiesDataHtml = '<div class="row justify-content-center align-items-center mx-3">\n' +
            '                    <div class="modal-sec"></div>\n' +
            '                </div>'
        let row = citiesData.find('.row')
        if (row.prop('outerHTML') === citiesDataHtml){
            mainSection.find('.main-body').removeClass('move-up').addClass('move-down')
            mainSection.find('.new-line-btn').addClass('d-none')
            mainSection.find('.new-line-row').addClass('d-none')
        }

        // $.ajax({
        //     // url: '{% url 'weather:remove_city' %}',
        //     method: 'POST',
        //     data: form.serialize(),
        //     success: function (data) {
        //         let cityCard = $this.closest('.city-card')
        //         cityCard.remove()
        //     },
        //     error: function (errorData) {
        //         console.log(errorData)
        //     }
        // })
    })


    //modal trigger
    let modalSec = $('.modal-sec')
    citiesData.on('click', '.card-detail', function (event) {

        let $this = $(this)
        let cityCard = $this.parent()
        let form = cityCard.find('form')
        modalSec.html()
        let modalBtn = modalSec.find('#modal-btn')
        modalBtn.click()
        modalSec.find('.square').eq("0").click()
        console.log('success')
        // $.ajax({
        //     // url: '{% url 'weather:modal-detail' %}',
        //     method: 'POST',
        //     data: form.serialize(),
        //     success: function (data) {
        //         modalSec.html(data.modalRender)
        //         let modalBtn = modalSec.find('#modal-btn')
        //         modalBtn.click()
        //         modalSec.find('.square').eq("0").click()
        //         console.log('success')
        //     },
        //     error: function (errorData) {
        //         console.log('error')
        //         console.log(errorData)
        //     }
        // })
    })

    //day inside modal
    modalSec.on('click', '.day', function (event) {
        let $this = $(this)

        let squareLight = modalSec.find('.square-light')
        let day = squareLight.parentsUntil('.days').eq(1)
        day.addClass('day2')
        day.find('.triangle-down').addClass('d-none')
        squareLight.removeClass('square-light')
        //
        let square = $this.find('.square')
        square.addClass('square-light')
        $this.find('.triangle-down').removeClass('d-none')
        $this.removeClass('day2')
        //
        // let hour = modalSec.find('.hour')
        // let selectedDate = $this.attr('data-date')
        // let j = 0
        // $.each(hour, function (i, element) {
        //     let $element = $(element)
        //     if (($element.attr('data-date') == selectedDate) || ((0 < j) && (j < 8))){
        //         $element.removeClass('d-none')
        //         j++
        //     }else{
        //         console.log('hello')
        //         $element.addClass('d-none')
        //     }
        // })
    })
})