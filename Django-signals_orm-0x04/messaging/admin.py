from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import Message, Notification


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    """
    Admin interface for Message model.
    """
    list_display = [
        'id',
        'sender_link',
        'receiver_link',
        'content_preview',
        'timestamp',
        'is_read',
        'notification_count'
    ]
    list_filter = [
        'is_read',
        'timestamp',
        'sender',
        'receiver'
    ]
    search_fields = [
        'sender__username',
        'receiver__username',
        'content'
    ]
    date_hierarchy = 'timestamp'
    readonly_fields = ['timestamp', 'notification_count']
    raw_id_fields = ['sender', 'receiver']

    # Custom ordering
    ordering = ['-timestamp']

    # Fields to display in the form
    fields = [
        'sender',
        'receiver',
        'content',
        'is_read',
        'timestamp',
        'notification_count'
    ]

    def sender_link(self, obj):
        """Create a link to the sender's admin page."""
        url = reverse('admin:auth_user_change', args=[obj.sender.id])
        return format_html('<a href="{}">{}</a>', url, obj.sender.username)
    sender_link.short_description = 'Sender'

    def receiver_link(self, obj):
        """Create a link to the receiver's admin page."""
        url = reverse('admin:auth_user_change', args=[obj.receiver.id])
        return format_html('<a href="{}">{}</a>', url, obj.receiver.username)
    receiver_link.short_description = 'Receiver'

    def content_preview(self, obj):
        """Show a preview of the message content."""
        if len(obj.content) > 50:
            return obj.content[:50] + '...'
        return obj.content
    content_preview.short_description = 'Content Preview'

    def notification_count(self, obj):
        """Show the number of notifications for this message."""
        count = obj.notifications.count()
        if count > 0:
            url = reverse('admin:messaging_notification_changelist') + f'?message__id={obj.id}'
            return format_html('<a href="{}">{} notification(s)</a>', url, count)
        return '0 notifications'
    notification_count.short_description = 'Notifications'

    # Add custom actions
    actions = ['mark_as_read', 'mark_as_unread']

    def mark_as_read(self, request, queryset):
        """Mark selected messages as read."""
        updated = queryset.update(is_read=True)
        self.message_user(request, f'{updated} messages marked as read.')
    mark_as_read.short_description = 'Mark selected messages as read'

    def mark_as_unread(self, request, queryset):
        """Mark selected messages as unread."""
        updated = queryset.update(is_read=False)
        self.message_user(request, f'{updated} messages marked as unread.')
    mark_as_unread.short_description = 'Mark selected messages as unread'


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """
    Admin interface for Notification model.
    """
    list_display = [
        'id',
        'user_link',
        'notification_type',
        'title',
        'content_preview',
        'is_read',
        'created_at',
        'related_message_link'
    ]
    list_filter = [
        'notification_type',
        'is_read',
        'created_at',
        'user'
    ]
    search_fields = [
        'user__username',
        'title',
        'content',
        'message__content'
    ]
    date_hierarchy = 'created_at'
    readonly_fields = ['created_at', 'related_message_link']
    raw_id_fields = ['user', 'message']

    # Custom ordering
    ordering = ['-created_at']

    # Fields to display in the form
    fields = [
        'user',
        'notification_type',
        'title',
        'content',
        'message',
        'is_read',
        'created_at',
        'related_message_link'
    ]

    def user_link(self, obj):
        """Create a link to the user's admin page."""
        url = reverse('admin:auth_user_change', args=[obj.user.id])
        return format_html('<a href="{}">{}</a>', url, obj.user.username)
    user_link.short_description = 'User'

    def content_preview(self, obj):
        """Show a preview of the notification content."""
        if len(obj.content) > 60:
            return obj.content[:60] + '...'
        return obj.content
    content_preview.short_description = 'Content Preview'

    def related_message_link(self, obj):
        """Create a link to the related message if it exists."""
        if obj.message:
            url = reverse(
                'admin:messaging_message_change',
                args=[obj.message.id]
                )
            return format_html(
                '<a href="{}">Message #{}</a>',
                url, obj.message.id
                )
        return 'No related message'
    related_message_link.short_description = 'Related Message'

    # Add custom actions
    actions = ['mark_as_read', 'mark_as_unread', 'delete_read_notifications']

    def mark_as_read(self, request, queryset):
        """Mark selected notifications as read."""
        updated = queryset.update(is_read=True)
        self.message_user(request, f'{updated} notifications marked as read.')
    mark_as_read.short_description = 'Mark selected notifications as read'

    def mark_as_unread(self, request, queryset):
        """Mark selected notifications as unread."""
        updated = queryset.update(is_read=False)
        self.message_user(request, f'{updated} notifications marked as unread.')
    mark_as_unread.short_description = 'Mark selected notifications as unread'

    def delete_read_notifications(self, request, queryset):
        """Delete notifications that have been read."""
        read_notifications = queryset.filter(is_read=True)
        count = read_notifications.count()
        read_notifications.delete()
        self.message_user(request, f'{count} read notifications deleted.')
    delete_read_notifications.short_description = 'Delete read notifications'

    # Customize the admin form
    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        queryset = super().get_queryset(request)
        return queryset.select_related('user', 'message')


# Admin site customization
admin.site.site_header = 'Messaging System Administration'
admin.site.site_title = 'Messaging Admin'
admin.site.index_title = 'Welcome to Messaging Administration'
