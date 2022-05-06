function drawChart(){

    var purchs = JSON.parse(items);
    var usersA = JSON.parse(users);
    console.log("drawChart")
    //Sorteren van de aankopen en users op datum
    purchs = purchs.sort((a,b) => new Date(b.date) - new Date(a.date))
    usersA = usersA.sort((a,b) => new Date(b.date) - new Date(a.date))
    //Nog omdraaien want gebeurd van groot naar klein
    purchs = purchs.reverse();
    usersA = usersA.reverse();
    smallesDatePurch = new Date(purchs[0].date);
    smallesDateUsers = new Date(usersA[0].date);
    biggestDatePurch = new Date(purchs[purchs.length-1].date);
    biggestDateUsers = new Date(usersA[usersA.length-1].date);
    begin = new Date(Math.min.apply(null, [ smallesDatePurch, smallesDateUsers]))
    end = new Date(Math.max.apply(null, [ biggestDatePurch, biggestDateUsers]))
    var dates = []
    var purchases = []
    var datesPurch = []
    var totalPurchases = 0
    var users_ = []
    var datesUsers = []
    var totalUsers = 0
    var allDates = []
    //We vullen alle beschikbare date in
    for (i=0; i < purchs.length; i++){
        datesPurch.push(purchs[i].date)
        purchases.push(purchs[i].purchases)
        totalPurchases += purchs[i].purchases
    }
    for (i=0; i < usersA.length; i++){
        datesUsers.push(usersA[i].date)
        users_.push(usersA[i].active_users)
        totalUsers += usersA[i].active_users
    }
    var count = 0
    for (i=begin; i<=end; i.setDate(i.getDate() + 1)){
        var curDate = i.toISOString().split('T')[0]
        allDates.push(curDate)

        if (!datesUsers.includes(curDate)){
            users_.splice(count,0,0)
        }

        if (!datesPurch.includes(curDate)){
            purchases.splice(count,0,0)
        }
        count++;
    }
    // document.write(jsonstr)
    var ctx = document.getElementById("myChart");
    var myChart = new Chart(ctx, {
      type: 'line',
      data: {
        labels: allDates,
        datasets: [
          {
            data: purchases,
              label :'Total purchases: ' + totalPurchases,
              borderColor: "#3e95cd",
              fill: false
          },
          {
            data: users_,
              label :'Total active users: ' + totalUsers,
              borderColor: "#cd3e3e",
              fill: false
          },
        ]
      }
    });
}
