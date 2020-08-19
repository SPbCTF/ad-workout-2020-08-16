var example3Left = document.getElementById('left-list'),
	example3Right = document.getElementById('center-list');

new Sortable(example3Left, {
	group: {
		name: 'shared',
		pull: 'clone'
	},
	animation: 150,
	sort: false,
	onEnd: function (evt) {
		if (evt.to.id == "center-list" && evt.from.id == "left-list"){
			$('.col_center').css('background-image','none');
			task_recieve(evt.item.id);
		};
	},
}
);


new Sortable(example3Right, {
	group: {
		name: 'shared',
	},
    animation: 150,
    onEnd: ({ item, originalEvent: { clientX, clientY } }) => {
        const { top, right, bottom, left } = example3Right.getBoundingClientRect(),
			droppedOutside = (clientY < top || clientX < left || clientY > bottom || clientX > right);

        if (droppedOutside) {
			item.parentNode.removeChild(item);
			$("#Name").hide();
			$("#Description").hide();
			$("#Flag").hide();
			$("#save_button").hide();
		}
	}
	
});
