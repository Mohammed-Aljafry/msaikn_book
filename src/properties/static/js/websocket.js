/**
 * إدارة اتصالات WebSocket للعقارات
 * يوفر واجهة برمجية للتفاعل مع العقارات في الوقت الفعلي
 */

class PropertyWebSocket {
    constructor() {
        // إنشاء اتصال WebSocket
        this.socket = new WebSocket(
            `${window.location.protocol === 'https:' ? 'wss:' : 'ws:'}//${window.location.host}/ws/properties/`
        );

        // تسجيل معالجات الأحداث
        this.socket.onopen = this.onOpen.bind(this);
        this.socket.onclose = this.onClose.bind(this);
        this.socket.onmessage = this.onMessage.bind(this);
        this.socket.onerror = this.onError.bind(this);

        // تخزين معالجات الأحداث المخصصة
        this.eventHandlers = {
            'property_created': [],
            'property_updated': [],
            'property_deleted': [],
            'property_liked': [],
            'comment_added': [],
            'comment_liked': [],
            'search_results': []
        };
    }

    /**
     * إرسال بيانات عبر WebSocket
     * @param {Object} data - البيانات المراد إرسالها
     */
    send(data) {
        if (this.socket.readyState === WebSocket.OPEN) {
            this.socket.send(JSON.stringify(data));
        } else {
            console.error('WebSocket connection is not open');
        }
    }

    /**
     * إنشاء عقار جديد
     * @param {Object} propertyData - بيانات العقار
     */
    createProperty(propertyData) {
        this.send({
            action: 'create_property',
            property: propertyData
        });
    }

    /**
     * تحديث عقار
     * @param {number} propertyId - معرف العقار
     * @param {Object} propertyData - بيانات العقار المحدثة
     */
    updateProperty(propertyId, propertyData) {
        this.send({
            action: 'update_property',
            property_id: propertyId,
            property: propertyData
        });
    }

    /**
     * حذف عقار
     * @param {number} propertyId - معرف العقار
     */
    deleteProperty(propertyId) {
        this.send({
            action: 'delete_property',
            property_id: propertyId
        });
    }

    /**
     * البحث في العقارات
     * @param {Object} searchCriteria - معايير البحث
     */
    searchProperties(searchCriteria) {
        this.send({
            action: 'search_properties',
            ...searchCriteria
        });
    }

    /**
     * إضافة إعجاب لعقار
     * @param {number} propertyId - معرف العقار
     */
    likeProperty(propertyId) {
        this.send({
            action: 'like_property',
            property_id: propertyId
        });
    }

    /**
     * إضافة تعليق على عقار
     * @param {number} propertyId - معرف العقار
     * @param {string} content - محتوى التعليق
     */
    addComment(propertyId, content) {
        this.send({
            action: 'add_comment',
            property_id: propertyId,
            content: content
        });
    }

    /**
     * تسجيل معالج حدث مخصص
     * @param {string} event - نوع الحدث
     * @param {Function} handler - دالة المعالجة
     */
    on(event, handler) {
        if (this.eventHandlers[event]) {
            this.eventHandlers[event].push(handler);
        }
    }

    /**
     * معالجة فتح الاتصال
     */
    onOpen() {
        console.log('WebSocket connection established');
    }

    /**
     * معالجة إغلاق الاتصال
     */
    onClose() {
        console.log('WebSocket connection closed');
        // إعادة الاتصال بعد 5 ثواني
        setTimeout(() => {
            console.log('Attempting to reconnect...');
            this.socket = new WebSocket(
                `${window.location.protocol === 'https:' ? 'wss:' : 'ws:'}//${window.location.host}/ws/properties/`
            );
        }, 5000);
    }

    /**
     * معالجة استلام رسالة
     * @param {MessageEvent} event - حدث الرسالة
     */
    onMessage(event) {
        const data = JSON.parse(event.data);
        const action = data.action;

        // استدعاء معالجات الأحداث المخصصة
        if (this.eventHandlers[action]) {
            this.eventHandlers[action].forEach(handler => handler(data));
        }
    }

    /**
     * معالجة الأخطاء
     * @param {Event} error - حدث الخطأ
     */
    onError(error) {
        console.error('WebSocket error:', error);
    }
}

// إنشاء كائن عام للاستخدام في الصفحات
window.propertySocket = new PropertyWebSocket();
