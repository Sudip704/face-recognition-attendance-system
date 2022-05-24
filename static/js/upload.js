// upload button code

const button = document.querySelector('.button');
const submit = document.querySelector('.submit');
const name1 = document.querySelector('#name')
const roll = document.querySelector('#roll')
const image = document.querySelector('#image')

function toggleClass() {
	if(name1.value!="" && roll.value!="" && image.files.length>0)
	this.classList.toggle('active');
}

function addClass() {
	this.classList.add('finished');
}

button.addEventListener('click', toggleClass);
button.addEventListener('transitionend', toggleClass);
button.addEventListener('transitionend', addClass);

//choose file button

function readURL(input) {
	if (input.files && input.files[0]) {
  
	  var reader = new FileReader();
  
	  reader.onload = function(e) {
		$('.image-upload-wrap').hide();
  
		$('.file-upload-image').attr('src', e.target.result);
		$('.file-upload-content').show();
  
		$('.image-title').html(input.files[0].name);
	  };
  
	  reader.readAsDataURL(input.files[0]);
  
	} else {
	  removeUpload();
	}
  }
  
  function removeUpload() {
	$('.file-upload-input').replaceWith($('.file-upload-input').clone());
	$('.file-upload-content').hide();
	$('.image-upload-wrap').show();
  }
  $('.image-upload-wrap').bind('dragover', function () {
	  $('.image-upload-wrap').addClass('image-dropping');
	});
	$('.image-upload-wrap').bind('dragleave', function () {
	  $('.image-upload-wrap').removeClass('image-dropping');
  });