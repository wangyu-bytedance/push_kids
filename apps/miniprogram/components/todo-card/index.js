Component({
  properties: { group: { type: Object, value: {} } },
  methods: {
    practice() {
      this.triggerEvent("practice", {
        reviewIds: (this.data.group.items || []).map((item) => item.review_id)
      });
    },
    feedback(event) {
      this.triggerEvent("feedback", {
        reviewId: event.currentTarget.dataset.reviewId,
        action: event.currentTarget.dataset.action
      });
    }
  }
});
