(function () {
  function setDisabled(el, disabled) {
    if (!el) return;
    el.disabled = disabled;
    if (el.tagName === "INPUT" || el.tagName === "TEXTAREA") {
      el.readOnly = disabled;
    }
  }

  function byIdOrName(id, name) {
    return (
      document.getElementById(id) || document.querySelector('[name="' + name + '"]')
    );
  }

  function clearField(el) {
    if (!el) return;
    if (el.tagName === "SELECT") {
      el.value = "";
    } else {
      el.value = "";
    }
  }

  function fillFromSubscription(subscription) {
    var name = byIdOrName("id_name", "name");
    var category = byIdOrName("id_category", "category");
    var amount = byIdOrName("id_amount", "amount");
    var currency = byIdOrName("id_currency", "currency");
    var transactionDate = byIdOrName("id_transaction_date", "transaction_date");

    if (name && subscription.name) {
      name.value = subscription.name;
    }
    if (category && subscription.category_id) {
      category.value = String(subscription.category_id);
    }
    if (amount && subscription.amount) {
      amount.value = subscription.amount;
    }
    if (currency && subscription.currency) {
      currency.value = subscription.currency;
    }
    if (transactionDate && subscription.transaction_date) {
      transactionDate.value = subscription.transaction_date;
    }
  }

  function toggleSubscriptionFields() {
    var subscription = byIdOrName("id_subscription", "subscription");
    if (!subscription) return;

    var hasSubscription = Boolean(subscription.value);
    var source = byIdOrName("id_source", "source");
    var name = byIdOrName("id_name", "name");
    var category = byIdOrName("id_category", "category");
    var amount = byIdOrName("id_amount", "amount");
    var currency = byIdOrName("id_currency", "currency");
    var transactionDate = byIdOrName("id_transaction_date", "transaction_date");
    var infoUrl =
      subscription.getAttribute("data-subscription-info-url") ||
      "/admin/subscriptions/expense/subscription-info/";

    if (hasSubscription && source) {
      source.value = "subscription";
    }

    setDisabled(source, hasSubscription);
    setDisabled(name, hasSubscription);
    setDisabled(category, hasSubscription);
    setDisabled(amount, hasSubscription);
    setDisabled(currency, hasSubscription);
    setDisabled(transactionDate, hasSubscription);

    if (!hasSubscription) {
      clearField(name);
      clearField(category);
      clearField(amount);
      clearField(currency);
      clearField(transactionDate);
      if (source) source.value = "manual";
      return;
    }

    if (infoUrl) {
      fetch(infoUrl.replace(/\/$/, "") + "/" + subscription.value + "/")
        .then(function (response) {
          if (!response.ok) throw new Error("Failed to fetch subscription");
          return response.json();
        })
        .then(function (data) {
          fillFromSubscription(data);
        })
        .catch(function () {});
    }
  }

  document.addEventListener("DOMContentLoaded", toggleSubscriptionFields);
  document.addEventListener("change", function (event) {
    if (event.target && event.target.id === "id_subscription") {
      toggleSubscriptionFields();
    }
  });
})();
