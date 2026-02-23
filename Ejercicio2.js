// 2.1
db.transactions.aggregate([
  {
    $group: {
      _id: "$account_id",
      tx_count: { $sum: 1 },
      avg_amount: { $avg: "$amount" }
    }
  },
  {
    $lookup: {
      from: "accounts",
      localField: "_id",
      foreignField: "account_id",
      as: "acc"
    }
  },
  { $unwind: "$acc" },
  {
    $lookup: {
      from: "customers",
      localField: "acc.customer_id",
      foreignField: "customer_id",
      as: "cust"
    }
  },
  { $unwind: "$cust" },
  {
    $group: {
      _id: "$cust.customer_id",
      full_name: {
        $first: {
          $trim: { input: { $concat: ["$cust.name.first", " ", "$cust.name.last"] } }
        }
      },
      city: { $first: "$cust.address.city" },
      total_transactions: { $sum: "$tx_count" },
      avg_transaction_amount: { $avg: "$avg_amount" }
    }
  },
  { $sort: { total_transactions: -1 } },
  {
    $project: {
      _id: 0,
      full_name: 1,
      city: 1,
      total_transactions: 1,
      avg_transaction_amount: { $round: ["$avg_transaction_amount", 2] }
    }
  }
]);

// 2.2
db.accounts.aggregate([
  {
    $group: {
      _id: "$customer_id",
      total_balance: { $sum: "$balance" }
    }
  },
  {
    $lookup: {
      from: "customers",
      localField: "_id",
      foreignField: "customer_id",
      as: "cust"
    }
  },
  { $unwind: "$cust" },
  {
    $addFields: {
      full_name: {
        $trim: { input: { $concat: ["$cust.name.first", " ", "$cust.name.last"] } }
      },
      category: {
        $switch: {
          branches: [
            { case: { $lt: ["$total_balance", 5000] }, then: "Bajo" },
            {
              case: {
                $and: [
                  { $gte: ["$total_balance", 5000] },
                  { $lte: ["$total_balance", 20000] }
                ]
              },
              then: "Medio"
            }
          ],
          default: "Alto"
        }
      }
    }
  },
  { $project: { _id: 0, full_name: 1, category: 1, total_balance: 1 } }
]);

// 2.3
db.accounts.aggregate([
  { $group: { _id: "$customer_id", total_balance: { $sum: "$balance" } } },
  {
    $lookup: {
      from: "customers",
      localField: "_id",
      foreignField: "customer_id",
      as: "cust"
    }
  },
  { $unwind: "$cust" },
  {
    $addFields: {
      full_name: {
        $trim: { input: { $concat: ["$cust.name.first", " ", "$cust.name.last"] } }
      },
      city: "$cust.address.city"
    }
  },
  { $sort: { city: 1, total_balance: -1 } },
  {
    $group: {
      _id: "$city",
      full_name: { $first: "$full_name" },
      total_balance: { $first: "$total_balance" }
    }
  },
  { $project: { _id: 0, city: "$_id", full_name: 1, total_balance: 1 } },
  { $sort: { total_balance: -1 } }
]);

// 2.4
db.transactions.aggregate([
  {
    $match: {
      date: { $gte: new Date(new Date().setMonth(new Date().getMonth() - 6)) }
    }
  },
  { $sort: { amount: -1 } },
  { $limit: 10 },
  {
    $lookup: {
      from: "accounts",
      localField: "account_id",
      foreignField: "account_id",
      as: "acc"
    }
  },
  { $unwind: "$acc" },
  {
    $lookup: {
      from: "customers",
      localField: "acc.customer_id",
      foreignField: "customer_id",
      as: "cust"
    }
  },
  { $unwind: "$cust" },
  {
    $addFields: {
      customer_name: {
        $trim: { input: { $concat: ["$cust.name.first", " ", "$cust.name.last"] } }
      },
      city: "$cust.address.city",
      email: "$cust.email"
    }
  },
  {
    $project: {
      _id: 0,
      date: 1,
      amount: 1,
      transaction_code: 1,
      symbol: 1,
      account_id: 1,
      customer_name: 1,
      city: 1,
      email: 1
    }
  }
]);

//2.5
db.transactions.aggregate([
  {
    $lookup: {
      from: "accounts",
      localField: "account_id",
      foreignField: "account_id",
      as: "acc"
    }
  },
  { $unwind: "$acc" },
  { $sort: { "acc.customer_id": 1, date: 1 } },
  {
    $group: {
      _id: "$acc.customer_id",
      tx_count: { $sum: 1 },
      oldest_amount: { $first: "$amount" },
      newest_amount: { $last: "$amount" }
    }
  },
  { $match: { tx_count: { $gte: 2 } } },
  {
    $addFields: {
      pct_change: {
        $cond: [
          { $eq: ["$oldest_amount", 0] },
          null,
          {
            $multiply: [
              { $divide: [{ $subtract: ["$newest_amount", "$oldest_amount"] }, "$oldest_amount"] },
              100
            ]
          }
        ]
      }
    }
  },
  {
    $lookup: {
      from: "customers",
      localField: "_id",
      foreignField: "customer_id",
      as: "cust"
    }
  },
  { $unwind: "$cust" },
  {
    $project: {
      _id: 0,
      full_name: {
        $trim: { input: { $concat: ["$cust.name.first", " ", "$cust.name.last"] } }
      },
      tx_count: 1,
      oldest_amount: 1,
      newest_amount: 1,
      pct_change: { $round: ["$pct_change", 2] }
    }
  },
  { $sort: { pct_change: -1 } }
]);