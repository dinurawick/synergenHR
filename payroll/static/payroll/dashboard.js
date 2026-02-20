staticUrl = $("#statiUrl").attr("data-url");

$(document).ready(function () {
  var myDate = new Date();
  var year = myDate.getFullYear();
  var month = myDate.getMonth() + 1; // getMonth() returns 0-11, so add 1
  
  // If current month is January, show December of previous year
  if (month === 1) {
    month = 12;
    year = year - 1;
  } else {
    month = month - 1; // Show previous month
  }
  
  // Format month to always be 2 digits
  var monthStr = month < 10 ? "0" + month : month.toString();
  var formattedDate = year + "-" + monthStr;
  
  var start_index = 0;
  var per_page = 10;

  $("#monthYearField").val(formattedDate);

  function isChartEmpty(chartData) {
    if (!chartData) {
      return true;
    }
    for (let i = 0; i < chartData.length; i++) {
      const hasNonZeroValues = chartData[i].data.some((value) => value !== 0);
      if (hasNonZeroValues) {
        return false; // Return false if any non-zero value is found
      }
    }
    return true; // Return true if all values are zero
  }

  // Call functions after date picker is set with a small delay to ensure value is set
  setTimeout(function() {
    employee_chart_view();
    payslip_details();
    department_chart_view();
    employees_joined();
    contract_ending();
  }, 100);

  function employee_chart(dataSet, labels) {
    $("#employee_canvas_body").html('<canvas id="employeeChart"></canvas>');

    const employeeChart = document
      .getElementById("employeeChart")
      .getContext("2d");

    $.ajax({
      url: "/payroll/get-language-code",
      type: "GET",
      success: (response) => {
        const scaleXText = response.scale_x_text;
        const scaleYText = response.scale_y_text;

        const employeeChartData = {
          labels: labels,
          datasets: dataSet,
        };

        window["employeeChart"] = {};

        // Chart constructor
        var employeePayrollChart = new Chart(employeeChart, {
          type: "bar",
          data: employeeChartData,
          options: {
            scales: {
              x: {
                stacked: true,
                title: {
                  display: true,
                  text: scaleXText,
                  font: {
                    weight: "bold",
                    size: 16,
                  },
                },
              },
              y: {
                stacked: true,
                title: {
                  display: true,
                  text: scaleYText,
                  font: {
                    weight: "bold",
                    size: 16,
                  },
                },
              },
            },
          },
        });

        $("#employeeChart").on("click", function (event) {
          var activeBars = employeePayrollChart.getElementsAtEventForMode(
            event,
            "index",
            { intersect: true },
            true
          );

          if (activeBars.length > 0) {
            var clickedBarIndex = activeBars[0].index;
            var clickedLabel = employeeChartData.labels[clickedBarIndex];
            localStorage.removeItem("savedFilters");
            var selectedDate = $("#monthYearField").val();
            const [year, month] = selectedDate.split("-");
            window.location.href =
              "/payroll/view-payslip?month=" +
              month +
              "&year=" +
              year +
              "&search=" +
              clickedLabel;
          }
        });
      },
      error: (error) => {
        console.log("Error", error);
      },
    });
  }

  var employee_chart_view = (dataSet, labels) => {
    var period = $("#monthYearField").val();

    $.ajax({
      url: "/payroll/dashboard-employee-chart",
      type: "GET",
      dataType: "json",
      headers: {
        "X-Requested-With": "XMLHttpRequest",
      },
      data: {
        period: period,
      },
      success: (response) => {
        dataSet = response.dataset;
        labels = response.labels;
        employees = response.employees;

        $("#select_employee").html("");
        $("#select_employee").append("<option></option>");

        $.each(employees, function (key, item) {
          $("#select_employee").append(
            $("<option>", {
              value: item[0],
              text: item[1] + " " + item[2],
            })
          );
        });

        $.each(dataSet, function (key, item) {
          item["data"] = item.data.slice(start_index, start_index + per_page);
        });
        var values = Object.values(labels).slice(
          start_index,
          start_index + per_page
        );
        if (isChartEmpty(dataSet)) {
          $("#employee_canvas_body").html(
            `<div style="height: 310px; display:flex;align-items: center;justify-content: center;" class="">
                        <div style="" class="">
                        <img style="display: block;width: 70px;margin: 10px auto ;" src="${
                          staticUrl + "images/ui/no-money.png"
                        }" class="" alt=""/>
                        <h3 style="font-size:16px" class="oh-404__subtitle">${
                          response.message
                        }</h3>
                        </div>
                    </div>`
          );
        } else {
          employee_chart(dataSet, values);
        }
      },
      error: (error) => {
        console.log("Error", error);
      },
    });
  };

  function payslip_details() {
    var period = $("#monthYearField").val();
    $.ajax({
      url: "/payroll/dashboard-payslip-details",
      type: "GET",
      dataType: "json",
      headers: {
        "X-Requested-With": "XMLHttpRequest",
      },
      data: {
        period: period,
      },
      success: (response) => {
        $(".payslip-number").html(response.no_of_emp);
        $(".payslip-amount").html(response.total_amount);
      },
      error: (error) => {
        console.log("Error", error);
      },
    });
  }

  function department_chart_view() {
    var period = $("#monthYearField").val();
    function department_chart(dataSet, labels) {
      $("#department_canvas_body").html(
        '<canvas id="departmentChart"></canvas>'
      );

      const departmentChartData = {
        labels: labels,
        datasets: dataSet,
      };

      window["departmentChart"] = {};
      const departmentChart = document.getElementById("departmentChart");

      // chart constructor
      var departmentPayrollChart = new Chart(departmentChart, {
        type: "pie",
        data: departmentChartData,
      });

      $("#departmentChart").on("click", function (event) {
        var activeBars = departmentPayrollChart.getElementsAtEventForMode(
          event,
          "index",
          { intersect: true },
          true
        );

        if (activeBars.length > 0) {
          var clickedBarIndex = activeBars[0].index;
          var clickedLabel = departmentChartData.labels[clickedBarIndex];
          window.location.href = `/payroll/view-payslip?start_date=${$(
            "#monthYearField"
          ).val()}-01&department=${clickedLabel}`;
        }
      });
    }

    $.ajax({
      url: "/payroll/dashboard-department-chart",
      type: "GET",
      dataType: "json",
      headers: {
        "X-Requested-With": "XMLHttpRequest",
      },
      data: {
        period: period,
      },
      success: (response) => {
        dataSet = response.dataset;
        labels = response.labels;
        department_total = response.department_total;
        if (department_total.length != 0) {
          $("#department_total").html("");
          $("#department_total").show();
          $("#department_total_empty").hide();
          $.each(department_total, function (key, value) {
            $("#department_total").append(
              `<li class='department' style='cursor: pointer; padding: 8px 12px; margin: 4px 0; background: #f8f9fa; border-radius: 6px; border-left: 4px solid #8e9aaf; transition: all 0.2s ease; font-size: 14px;' onmouseover="this.style.background='#e9ecef'" onmouseout="this.style.background='#f8f9fa'">
                <i class="fas fa-building" style="color: #8e9aaf; margin-right: 8px;"></i>
                <span class='department_item'>${value["department"]}</span>: 
                <span style="color: #7fb069; font-weight: 600;"> ${value["amount"].toFixed(2)}</span>
              </li>`
            );
          });
        } else {
          $("#department_total").hide();
          $("#department_total_empty").show();
          $("#department_total_empty").html(
            `<div style="display:flex;align-items: center;justify-content: center; padding-top:50px" class="">
                        <div style="" class="">
                        <img style="display: block;width: 70px;margin: 10px auto ;" src="${
                          staticUrl + "images/ui/money.png"
                        }" class="" alt=""/>
                        <h3 style="font-size:16px" class="oh-404__subtitle">${
                          response.message
                        }</h3>
                        </div>
                    </div>`
          );
        }

        if (isChartEmpty(dataSet)) {
          $("#department_canvas_body").html(
            `<div style="height: 310px; display:flex;align-items: center;justify-content: center;" class="">
                        <div style="" class="">
                        <img style="display: block;width: 70px;margin: 10px auto ;" src="${
                          staticUrl + "images/ui/no-money.png"
                        }" class="" alt=""/>
                        <h3 style="font-size:16px" class="oh-404__subtitle">${
                          response.message
                        }</h3>
                        </div>
                    </div>`
          );
        } else {
          department_chart(dataSet, labels);
        }
      },
      error: (error) => {
        console.log("Error", error);
      },
    });
  }

  function employees_joined() {
    var period = $("#monthYearField").val();
    var date = period.split("-");
    var year = date[0];
    var month = parseInt(date[1]);

    var monthNames = [
      "January", "February", "March", "April", "May", "June",
      "July", "August", "September", "October", "November", "December",
    ];
    
    var monthName = monthNames[month - 1];

    $.ajax({
      url: "/payroll/dashboard-employees-joined",
      type: "GET",
      dataType: "json",
      headers: {
        "X-Requested-With": "XMLHttpRequest",
      },
      data: {
        period: period,
      },
      success: (response) => {
        var joined_employees = response.joined_employees;
        if (joined_employees.length != 0) {
          $("#employees_joined").html("");
          var activeCount = 0;
          var archivedCount = 0;
          
          $.each(joined_employees, function (key, value) {
            var id = value.employee_id;
            var contract_id = value.contract_id;
            var elem;
            
            // Get contract status colors - matching contract page colors
            var statusColors = {
              'active': '#7fb069',    // Green
              'draft': '#6c757d',     // Gray  
              'expired': '#dc3545',   // Red
              'terminated': '#0d6efd' // Dark Blue
            };
            
            var borderColor = statusColors[value.contract_status] || '#6c757d';
            var iconColor = borderColor;
            
            // Determine the link URL - use contract page if contract_id exists, otherwise employee view
            var linkUrl = contract_id ? `/payroll/update-contract/${contract_id}` : `/employee/employee-view/${id}/#tab_2`;
            
            if (value.is_active) {
              // Active employee - use contract status color
              activeCount++;
              elem = `<li class='employee_id' style="cursor: pointer; padding: 8px 12px; margin: 4px 0; background: #f8f9fa; border-radius: 6px; border-left: 4px solid ${borderColor}; transition: all 0.2s ease; font-size: 14px;" data-id=${id} onmouseover="this.style.background='#e9ecef'" onmouseout="this.style.background='#f8f9fa'" onclick="window.open('${linkUrl}', '_blank')"> 
                <i class="fas fa-user" style="color: ${iconColor}; margin-right: 8px;"></i><span style="text-decoration: underline; color: #007bff;">${value.employee_name}</span> 
                <span style="color: ${iconColor}; font-size: 11px; font-weight: 500; text-transform: capitalize;">(${value.contract_status})</span>
              </li>`;
            } else {
              // Archived employee - grayed out with contract status
              archivedCount++;
              elem = `<li class='employee_id archived' style="cursor: pointer; padding: 8px 12px; margin: 4px 0; background: #f5f5f5; border-radius: 6px; border-left: 4px solid ${borderColor}; transition: all 0.2s ease; font-size: 14px; opacity: 0.7;" data-id=${id} onmouseover="this.style.background='#e9ecef'; this.style.opacity='0.8'" onmouseout="this.style.background='#f5f5f5'; this.style.opacity='0.7'" onclick="window.open('${linkUrl}', '_blank')"> 
                <i class="fas fa-archive" style="color: #dc3545; margin-right: 8px;"></i><span style="text-decoration: underline; color: #007bff;">${value.employee_name}</span> 
                <span style="color: #dc3545; font-size: 12px; font-weight: 500;">(Archived)</span>
                <span style="color: ${iconColor}; font-size: 11px; font-weight: 500; text-transform: capitalize; margin-left: 4px;">[${value.contract_status}]</span>
              </li>`;
            }
            $("#employees_joined").append(elem);
          });
          
          // Update count display with breakdown
          var countText = `Number of employees joined in ${monthName} of ${year} : <span style="color: #7fb069; font-weight: 600;">${joined_employees.length}</span>`;
          if (archivedCount > 0) {
            countText += ` <span style="color: #6c757d; font-size: 13px;">(${activeCount} active, ${archivedCount} archived)</span>`;
          }
          $(".joined-full-text").html(countText);
        } else {
          $(".joined-full-text").html(`Number of employees joined in ${monthName} of ${year} : <span style="color: #7fb069; font-weight: 600;">${joined_employees.length}</span>`);
          $("#employees_joined").html(
            `<div style="display:flex;align-items: center;justify-content: center; padding-top:50px" class="">
              <div style="" class="">
                <img style="display: block;width: 70px;margin: 10px auto ;" src="${
                  staticUrl + "images/ui/user.png"
                }" class="" alt=""/>
                <h3 style="font-size:16px; color: #6c757d; text-align: center;" class="oh-404__subtitle">${
                  response.message
                }</h3>
              </div>
            </div>`
          );
        }
      },
      error: (error) => {
        console.log("Error", error);
      },
    });
  }

  function contract_ending() {
    var period = $("#monthYearField").val();
    var date = period.split("-");
    var year = date[0];
    var month = parseInt(date[1]);

    var monthNames = [
      "January",
      "February",
      "March",
      "April",
      "May",
      "June",
      "July",
      "August",
      "September",
      "October",
      "November",
      "December",
    ];
    
    var monthName = monthNames[month - 1];

    $.ajax({
      url: "/payroll/dashboard-contract-ending",
      type: "GET",
      dataType: "json",
      headers: {
        "X-Requested-With": "XMLHttpRequest",
      },
      data: {
        period: period,
      },
      success: (response) => {
        var contract_end = response.contract_end;
        if (contract_end.length != 0) {
          $("#contract_ending").html("");
          $.each(contract_end, function (key, value) {
            id = value.contract_id;
            elem = `<li class='contract_id' style="cursor: pointer; padding: 8px 12px; margin: 4px 0; background: #f8f9fa; border-radius: 6px; border-left: 4px solid #c85450; transition: all 0.2s ease; font-size: 14px;" data-id=${id} onmouseover="this.style.background='#e9ecef'" onmouseout="this.style.background='#f8f9fa'"> 
              <i class="fas fa-file-contract" style="color: #c85450; margin-right: 8px;"></i>${value.contract_name} 
            </li>`;

            $("#contract_ending").append(elem);
          });
          $(".contract-number").html(
            `${monthName} of ${year} : ${contract_end.length}`
          );
        } else {
          $(".contract-number").html(
            `${monthName} of ${year} : ${contract_end.length}`
          );
          $("#contract_ending").html(
            `<div style="display:flex;align-items: center;justify-content: center; padding-top:50px" class="">
              <div style="" class="">
                <img style="display: block;width: 70px;margin: 10px auto ;" src="${
                  staticUrl + "images/ui/contract.png"
                }" class="" alt=""/>
                <h3 style="font-size:16px; color: #6c757d; text-align: center;" class="oh-404__subtitle">${
                  response.message
                }</h3>
              </div>
            </div>`
          );
        }
      },
      error: (error) => {
        console.log("Error", error);
      },
    });
  }

  $("#monthYearField").on("change", function () {
    employee_chart_view();
    payslip_details();
    department_chart_view();
    employees_joined();
    contract_ending();
  });

  $("#payroll-employee-next").on("click", function () {
    var period = $("#monthYearField").val();
    $.ajax({
      url: "/payroll/dashboard-employee-chart",
      type: "GET",
      dataType: "json",
      headers: {
        "X-Requested-With": "XMLHttpRequest",
      },
      data: {
        period: period,
      },
      success: (response) => {
        dataSet = response.dataset;
        labels = response.labels;

        updated_data = dataSet;
        if (start_index == 0) {
          start_index += per_page;
        }
        $.each(updated_data, function (key, item) {
          item["data"] = item.data.slice(start_index, start_index + per_page);
        });

        var values = Object.values(labels).slice(
          start_index,
          start_index + per_page
        );
        if (values.length > 0) {
          employee_chart(updated_data, values);
          start_index += per_page;
        }
      },
      error: (error) => {
        console.log("Error", error);
      },
    });
  });

  $("#employee-previous").on("click", function () {
    var period = $("#monthYearField").val();
    $.ajax({
      url: "/payroll/dashboard-employee-chart",
      type: "GET",
      dataType: "json",
      headers: {
        "X-Requested-With": "XMLHttpRequest",
      },
      data: {
        period: period,
      },
      success: (response) => {
        dataSet = response.dataset;
        labels = response.labels;

        if (start_index <= 0) {
          return;
        }
        start_index -= per_page;
        if (start_index > 0) {
          updated_data = dataSet.map((item) => ({
            ...item,
            data: item.data.slice(start_index - per_page, start_index),
          }));
          var values = Object.values(labels).slice(
            start_index - per_page,
            start_index
          );
          employee_chart(updated_data, values);
        }
      },
      error: (error) => {
        console.log("Error", error);
      },
    });
  });

  $(".filter").on("click", function () {
    $("#back_button").removeClass("d-none");
  });

  $("#contract_ending").on("click", ".contract_id", function () {
    id = $(this).data("id");
    $.ajax({
      url: "/payroll/single-contract-view/" + id,
      type: "GET",
      dataType: "html",
      headers: {
        "X-Requested-With": "XMLHttpRequest",
      },
      data: {
        dashboard: "dashboard",
      },
      success: (response) => {
        $("#ContractModal").toggleClass("oh-modal--show");
        $("#contract_target").html(response);
      },
      error: (error) => {
        console.log("Error", error);
      },
    });
  });

  $("#ContractModal").on("click", ".oh-modal__close", function () {
    $("#ContractModal").removeClass("oh-modal--show");
  });

  $("#department_total").on("click", ".department", function () {
    department = $(this).children(".department_item").text();
    window.location.href = `/payroll/view-payslip?start_date=${$(
      "#monthYearField"
    ).val()}-01&department=${department}`;
  });
});
