/* 1.html */
function addCommas(input) {
    // Remove existing commas and non-numeric characters
    input.value = input.value.replace(/[^0-9]/g, '');
    // Add commas every three digits
    input.value = input.value.replace(/\B(?=(\d{3})+(?!\d))/g, ',');
}


/* 2.html */
//'학과' 동적 범위 변경
//아래는 코드 예시 - 이를 기반으로 변경할 것
function updateDepartments() {
    const facultySelect = document.getElementById('faculty');
    const departmentSelect = document.getElementById('department');
    departmentSelect.innerHTML = ''; // 기존 옵션 초기화

    const faculty = facultySelect.value;

    if (faculty === 'engineering') {
        addDepartmentOption(departmentSelect, 'computer', '컴퓨터공학');
        addDepartmentOption(departmentSelect, 'mechanical', '기계공학');
    } else if (faculty === 'science') {
        addDepartmentOption(departmentSelect, 'physics', '물리학');
        addDepartmentOption(departmentSelect, 'chemistry', '화학');
    } else if (faculty === 'business') {
        addDepartmentOption(departmentSelect, 'accounting', '회계학');
        addDepartmentOption(departmentSelect, 'marketing', '마케팅');
    }
}

function addDepartmentOption(select, value, text) {
    const option = document.createElement('option');
    option.value = value;
    option.text = text;
    select.appendChild(option);
}

// 초기 설정
updateDepartments();

//정렬
function sortby_regdate(){

}

function sortby_popular(){

}

function sortby_lowprice(){

}


/********3.html***********/
/*리뷰 또는 상세설명 보기 버튼 동작*/
document.addEventListener("DOMContentLoaded", function() {
    const reviewBtn = document.getElementById("review-btn");
    const descrBtn = document.getElementById("descr-btn");
    const reviewScreen = document.getElementById("review-screen");
    const descrScreen = document.getElementById("descr-screen");

    reviewBtn.addEventListener("click", function() {
        reviewScreen.style.display = "block";
        descrScreen.style.display = "none";
    });

    descrBtn.addEventListener("click", function() {
        reviewScreen.style.display = "none";
        descrScreen.style.display = "block";
    });
});
